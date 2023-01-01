"""Helper functions for the hibernate package.
"""

import base64
import json
import os
import sys

import sh

from hibernate import external
from hibernate import exceptions


def get_aws_creds_from_ocp():
    """Pull AWS credentials from the oc-hibernate secret in the kube-admin
    namespace (if it exists)."""
    try:
        aws_creds_secret = external.oc(
            "get",
            "secret",
            "oc-hibernate",
            "--namespace", "kube-system",
            "--output", "json"
        )
    except sh.ErrorReturnCode as exception:
        not_found_message = b'Error from server (NotFound): secrets "oc-hibernate" not found\n'
        if exception.stderr == not_found_message:
            raise exceptions.OpenShiftNotFound(exception)
        else:
            # An unknown error has occurred
            raise exception

    response = {}
    response['access_key'] = base64.b64decode(
        aws_creds_secret['data']['aws_access_key_id']
    ).decode('utf-8')
    response['secret_access_key'] = base64.b64decode(
        aws_creds_secret['data']['aws_secret_access_key']
    ).decode('utf-8')

    return response


def get_cluster_id():
    """Get cluster ID from running OpenShift cluster."""
    try:
        oc_cmd_output = sh.oc(
            "get",
            "machines",
            "-n", "openshift-machine-api",
            "-o", "json"
        )
    except sh.ErrorReturnCode as exception:
        print(exception.stdout.decode('utf-8'), end="")
        print_error(exception.stderr.decode('utf-8'), end="")
        sys.exit(1)

    oc_response = json.loads(oc_cmd_output.stdout)

    # Grab the cluster ID from the first machine. It doesn't matter what
    # machine the label is grabbed from. All machines share the same label.
    cluster_id = oc_response['items'][0]['metadata']['labels'] \
                            ['machine.openshift.io/cluster-api-cluster']

    # TODO: Maybe fail better here if no machines exist

    return cluster_id


def get_availible_cluster_ids(aws_profile):
    """Get cluster IDs of clusters in AWS. Looks at prefix on EC2 instance
    names to determine cluster ID.

    :param str aws_profile:
        Profile name is passed to AWS CLI
    """

    # Get master-0 node of every cluster available in the AWS region
    aws_cmd_output = sh.aws(
        'ec2',
        'describe-instances',
        '--filter', f'Name=tag:Name,Values=*-master-0',
        '--output', 'json',
        '--profile', aws_profile,
        _tty_out=False
    )
    aws_response = json.loads(aws_cmd_output.stdout)
    ec2_instances = [
        reservation["Instances"][0] for reservation in aws_response["Reservations"]
    ]

    # Create list of clusters by taking prefix from instance name as cluster_id
    clusters = []
    for ec2_instance in ec2_instances:
        name = "Unknown"
        for tag in ec2_instance["Tags"]:
            if tag['Key'] == "Name":
                name = tag['Value']
        # Split string and grab beginning of string up to master
        cluster_id = name.split('-master-')[0]
        clusters.append({'cluster_id': cluster_id})

    for cluster in clusters:
        # Get all machines for a given cluster
        aws_cmd_output = sh.aws(
            'ec2',
            'describe-instances',
            '--filter', f'Name=tag:Name,Values={cluster["cluster_id"]}-*',
            '--output', 'json',
            '--profile', aws_profile,
            _tty_out=False
        )
        aws_response = json.loads(aws_cmd_output.stdout)
        ec2_instances = [
            reservation["Instances"][0] for reservation in aws_response["Reservations"]
        ]

        # Get machine names and statuses
        machines = []
        for ec2_instance in ec2_instances:
            name = "Unknown"
            for tag in ec2_instance["Tags"]:
                if tag['Key'] == "Name":
                    name = tag['Value']
            state = ec2_instance['State']['Name']
            machines.append({
                "name": name,
                "state": state,
            })
        cluster['machines'] = machines

        # Compare individual machine statuses to determine overall cluster status
        cluster_state = machines[0]['state']
        for machine in machines:
            if machine['state'] != cluster_state:
                cluster_state = "mixed"
                break
        cluster["state"] = cluster_state

    return clusters


def get_resource_path(relative_path):
    """Get absolute path to resource. Works for dev and for PyInstaller.
    https://stackoverflow.com/a/31966932

    This is used for Ansible playbooks.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def run_preflight_checks():
    """Validate that prerequisites are installed."""

    # Validate Ansible is installed
    output = sh.ansible_playbook('--version')
    if output.exit_code != 0:
        print_error(
            'ERROR: "ansible_playbook" not found in $PATH.',
            'Install Ansible to use this plugin.'
        )
        sys.exit(1)

    # Validate AWS CLI is installed
    output = sh.aws('--version')
    if output.exit_code != 0:
        print_error(
            'ERROR: "aws" not found in $PATH.',
            'Install AWS CLI v2 to use this plugin.'
        )
        sys.exit(1)

    # Validate OpenShift CLI is installed
    output = sh.oc('version')
    if output.exit_code != 0:
        print_error(
            'ERROR: "oc" not found in $PATH.',
            'Install OpenShift CLI to use this plugin.'
        )
        sys.exit(1)


def print_error(*args, **kwargs):
    """Works like print(), but prints to stderr instead of stdout."""
    print(*args, file=sys.stderr, **kwargs)
