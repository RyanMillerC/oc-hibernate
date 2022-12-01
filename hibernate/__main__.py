import click

@click.command()
@click.option("--name", help="Will display in message")
def main(name):
    if name:
        print(f"Hello {name}!")
    else:
        print(f"Hello World!")
