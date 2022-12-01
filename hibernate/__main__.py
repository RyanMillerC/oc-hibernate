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
