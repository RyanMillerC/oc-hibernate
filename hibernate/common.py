"""Common functions used by more than one hibernate command."""

import base64
import json
import sys

import sh

from hibernate import external, exceptions, helper
from hibernate.types import Machine, OpenShiftCluster


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
        helper.print_error(exception.stderr.decode('utf-8'), end="")
        sys.exit(1)

    oc_response = json.loads(oc_cmd_output.stdout)

    # Grab the cluster ID from the first machine. It doesn't matter what
    # machine the label is grabbed from. All machines share the same label.
    cluster_id = oc_response['items'][0]['metadata']['labels'] \
                            ['machine.openshift.io/cluster-api-cluster']

    # TODO: Maybe fail better here if no machines exist

    return cluster_id


def get_available_cluster_ids(aws_profile):
    """Get cluster IDs of clusters in AWS. Looks at prefix on EC2 instance
    names to determine cluster ID.

    :param str aws_profile:
        Profile name is passed to AWS CLI

    :returns: List of clusters
    :rtype list:
    """
    # Get master-0 node of every cluster available in the AWS region
    aws_response = external.aws(
        "ec2",
        "describe-instances",
        "--filter", f"Name=tag:Name,Values=*-master-0",
        "--output", "json",
        "--profile", aws_profile
    )
    ec2_instances = [
        reservation["Instances"][0] for reservation in aws_response["Reservations"]
    ]

    # Create list of clusters by taking prefix from instance name as cluster_id
    clusters = []
    for ec2_instance in ec2_instances:
        for tag in ec2_instance["Tags"]:
            if tag['Key'] == "Name":
                name = tag['Value']
        # Split string and grab beginning of string up to master. That is the
        # ID of the cluster (cluster-name + random-id)
        cluster_id = name.split('-master-')[0]
        clusters.append(OpenShiftCluster(cluster_id))

    for cluster in clusters:
        # Get all machines for a given cluster
        aws_response = external.aws(
            "ec2",
            "describe-instances",
            "--filter", f'Name=tag:Name,Values={cluster.name}-*',
            "--output", "json",
            "--profile", aws_profile,
        )
        ec2_instances = [
            reservation["Instances"][0] for reservation in aws_response["Reservations"]
        ]

        # Get machine names and statuses
        for ec2_instance in ec2_instances:
            for tag in ec2_instance["Tags"]:
                if tag['Key'] == "Name":
                    name = tag['Value']
            state = ec2_instance['State']['Name']
            cluster.add_machine(Machine(name, state))

    # TODO: Return a Python type instead of this JSON-like mess
    return clusters
