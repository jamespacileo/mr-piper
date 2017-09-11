import click


@click.command()
def outdated():
    "Lists packages that have updates available"
    pass

@click.command()
@click.argument("package_names", nargs=-1)
def add(package_names):
    pass

@click.command()
@click.argument("package_names", nargs=-1)
def remove(package_names):
    pass

@click.command()
def install():
    pass

@click.command()
def init():
    click.echo("Initializing project")
    pass

@click.command()
@click.argument("package_names", nargs=-1)
def upgrade():
    pass

@click.command()
def hello():
    click.echo("Hello world!")
    