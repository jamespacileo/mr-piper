import click

@click.group()
def cli():
    pass

@cli.command()
def outdated():
    "Lists packages that have updates available"
    pass

@cli.command()
@click.argument("package_names", nargs=-1)
def add(package_names):
    "Install and add a package to requirements"
    pass

@cli.command()
@click.argument("package_names", nargs=-1)
def remove(package_names):
    "Remove a list of packages and their dependencies, and remove this from the requirements."
    pass

@cli.command()
@click.option("--dev", default=False, help="If to install dev packages")
def install(dev):
    "Install all packages in requirement files."
    pass

@cli.command()
def init():
    "Initialise project with virtual environment, requirements structure and package lock."
    click.echo("Initializing project")
    pass

@cli.command()
@click.argument("package_names", nargs=-1)
def upgrade():
    "Upgrade a list of packages."
    pass
    
if __name__ == '__main__':
    cli()