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
        oc_response = json.loads(oc_cmd_output.stdout)

        pending_csr_names = []
        for csr in oc_response["items"]:
            name = csr["metadata"]["name"]
            conditions = []
            if csr["status"]:
                for condition in csr["status"]["conditions"]:
                    conditions.append(condition["type"])
            else:
                conditions.append("Pending")
            if "Pending" in conditions:
                pending_csr_names.append(name)

        oc_cmd_output = sh.oc(
            "adm",
            "certificate",
            "approve",
            *pending_csr_names,
            _in=sys.stdin,
            _out=sys.stdout
        )
    except Exception as exception:
        raise exception

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
@click.argument("CLUSTER_ID")
def stop(cluster_id):
    playbook_path = helper.get_resource_path('playbooks/stop.yml')
    sh.ansible_playbook(
        playbook_path,
        "--extra-vars", f'cluster_id="{cluster_id}"',
        _in=sys.stdin,
        _out=sys.stdout
    )
cli.add_command(stop)
