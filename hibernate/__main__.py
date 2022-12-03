"""Main module for hibernate. Hibernate uses the click CLI package. The main
command `oc-hibernate` does nothing except perform preflight checks. The
subcommands `oc-hibernate COMMAND` actually perform functions.
"""

import json
import sys

import click
import sh

from hibernate import helper


@click.group(help="Stop and resume OpenShift clusters in AWS")
def cli():
    helper.run_preflight_checks()


@click.command(help="Approve new certificates to replace certs that expired while the cluster was stopped")
def fix_certs():
    try:
        oc_cmd_output = sh.oc("get", "csr", "-o", "json")
    except sh.ErrorReturnCode as exception:
        print(exception.stdout.decode('utf-8'), end="")
        helper.print_error(exception.stderr.decode('utf-8'), end="")
        sys.exit(1)

    oc_response = json.loads(oc_cmd_output.stdout)

    # Check each CSR for Pending status
    pending_csr_names = []
    for csr in oc_response["items"]:
        name = csr["metadata"]["name"]
        conditions = []
        if csr["status"] and csr["status"]["conditions"]:
            for condition in csr["status"]["conditions"]:
                conditions.append(condition["type"])
        else:
            # CSRs without a status/condition are assumed to be pending
            conditions.append("Pending")
        if "Pending" in conditions:
            pending_csr_names.append(name)

    if len(pending_csr_names) == 0:
        print('No CSRs to approve!')
        sys.exit()

    # Approve all pending CSRs
    try:
        oc_cmd_output = sh.oc(
            "adm",
            "certificate",
            "approve",
            *pending_csr_names,
            _in=sys.stdin,
            _out=sys.stdout
        )
    except sh.ErrorReturnCode as exception:
        print(exception.stdout.decode('utf-8'), end="")
        helper.print_error(exception.stderr.decode('utf-8'), end="")
        sys.exit(1)
cli.add_command(fix_certs)


@click.command(help="Print status of cluster machines")
@click.argument("CLUSTER_ID")
def status(cluster_id):
    aws_cmd_output = sh.aws(
        'ec2',
        'describe-instances',
        '--filter', f'Name=tag:Name,Values={cluster_id}-*',
        '--output', 'json',
        _tty_out=False
    )
    aws_response = json.loads(aws_cmd_output.stdout)
    ec2_instances = [
        reservation["Instances"][0] for reservation in aws_response["Reservations"]
    ]

    filtered_instances = []
    for ec2_instance in ec2_instances:
        name = "Unknown"
        for tag in ec2_instance["Tags"]:
            if tag['Key'] == "Name":
                name = tag['Value']
        state = ec2_instance['State']['Name']
        filtered_instances.append({
            "Name": name,
            "State": state,
        })

    template = "{Name:50}{State:10}"
    print(template.format(Name="NAME", State="STATE"))
    for instance in filtered_instances:
        print(template.format(**instance))
cli.add_command(status)


@click.command(help="Resume (start up) a cluster")
@click.argument("CLUSTER_ID")
def start(cluster_id):
    playbook_path = helper.get_resource_path('playbooks/start.yml')
    sh.ansible_playbook(
        playbook_path,
        "--extra-vars", f'cluster_id="{cluster_id}"',
        _in=sys.stdin,
        _out=sys.stdout
    )
cli.add_command(start)


@click.command(help="Stop (shut down) a cluster")
@click.option(
    "--cluster-id",
    help="Manually set cluster ID (Defaults to pulling ID from OpenShift)"
)
def stop(cluster_id):
    if not cluster_id:
        cluster_id = get_cluster_id()
    playbook_path = helper.get_resource_path('playbooks/stop.yml')
    sh.ansible_playbook(
        playbook_path,
        "--extra-vars", f'cluster_id="{cluster_id}"',
        _in=sys.stdin,
        _out=sys.stdout
    )
cli.add_command(stop)


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


def get_availible_cluster_ids():
    """Get cluster IDs of clusters in AWS. Looks at prefix on EC2 instance
    names to determine cluster ID.
    """
    aws_cmd_output = sh.aws(
        'ec2',
        'describe-instances',
        '--filter', f'Name=tag:Name,Values=*-master-*',
        '--output', 'json',
        _tty_out=False
    )
    aws_response = json.loads(aws_cmd_output.stdout)
    ec2_instances = [
        reservation["Instances"][0] for reservation in aws_response["Reservations"]
    ]

    cluster_ids = []
    for ec2_instance in ec2_instances:
        name = "Unknown"
        for tag in ec2_instance["Tags"]:
            if tag['Key'] == "Name":
                name = tag['Value']
        # Split string and grab beginning of string up to master
        cluster_id = name.split('-master-')[0]
        if not cluster_id in cluster_ids:
            cluster_ids.append(cluster_id)

    return cluster_ids
