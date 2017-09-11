import click
import os

import piper

@click.group()
def cli():
    pass

@cli.command()
def outdated():
    "Lists packages that have updates available"
    piper.outdated()

@cli.command()
@click.option("--dev", is_flag=True)
@click.argument("package_names", nargs=-1)
def add(dev, package_names):
    "Install and add a package to requirements"
    for package_name in package_names:
        piper.add(package_name, dev=dev)

@cli.command()
@click.option("--dev", is_flag=True)
@click.argument("package_names", nargs=-1)
def remove(dev, package_names):
    "Remove a list of packages and their dependencies, and remove this from the requirements."
    for package_name in package_names:
        piper.remove(package_name, dev=dev)

@cli.command()
@click.option("--dev", is_flag=True, help="If to install dev packages")
def install(dev):
    "Install all packages in requirement files."
    piper.install()

@cli.command()
def init():
    "Initialise project with virtual environment, requirements structure and package lock."
    click.echo("Initializing project")
    piper.init()

@cli.command()
@click.argument("package_names", nargs=-1)
def upgrade():
    "Upgrade a list of packages."
    piper.upgrade()
    
@cli.command()
def clear():
    "Deletes virtualenv, requirements folder/files and piper file."
    piper.clear()

if __name__ == '__main__':
    os.chdir("..")
    cli()