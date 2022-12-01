import os
import sys

import click
import sh


# https://stackoverflow.com/a/31966932
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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
    print(f"STATUS GOES HERE")
cli.add_command(status)


@click.command(help="Unhibernate (start up) a cluster")
def start():
    playbook_path = resource_path('playbooks/test.yml')
    sh.ansible_playbook(playbook_path, _in=sys.stdin, _out=sys.stdout)
cli.add_command(start)


@click.command(help="Hibernate (shut down) a cluster")
def stop():
    print(f"STOP CLUSTER")
cli.add_command(stop)
