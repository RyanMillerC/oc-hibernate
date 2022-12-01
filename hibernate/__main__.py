import click


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
    print(f"START CLUSTER")
cli.add_command(start)


@click.command(help="Hibernate (shut down) a cluster")
def stop():
    print(f"STOP CLUSTER")
cli.add_command(stop)
