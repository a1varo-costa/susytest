import click

@click.command()
def cli(nodiff):
    """A script to automate the testing of programs to be
    submitted to Unicamp's SuSy platform."""
    click.echo("Hello")