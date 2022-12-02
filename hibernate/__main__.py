import json
import sys

import click
import sh

from hibernate import helper


@click.group(help="Hibernate (Start/Stop) OpenShift clusters")
def cli():
    pass


@click.command(name="print", help="Print a message")
@click.option("--name", help="Name to display in message")
def print_message(name):
    if name:
        print(f"Hello {name}!")
    else:
        print(f"Hello World!")
cli.add_command(print_message)


@click.command(help="Print hibernation status")
def status():
    aws_cmd_output = sh.aws('ec2', 'describe-instances', '--output', 'json', _tty_out=False)
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


@click.command(help="Unhibernate (start up) a cluster")
def start():
    playbook_path = helper.get_resource_path('playbooks/test.yml')
    sh.ansible_playbook(playbook_path, _in=sys.stdin, _out=sys.stdout)
cli.add_command(start)


@click.command(help="Hibernate (shut down) a cluster")
def stop():
    playbook_path = helper.get_resource_path('playbooks/test.yml')
    sh.ansible_playbook(playbook_path, _in=sys.stdin, _out=sys.stdout)
cli.add_command(stop)
