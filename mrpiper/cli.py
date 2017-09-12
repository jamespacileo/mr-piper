import click
import os

import sys
sys.path.append("..")
from mrpiper import piper

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
        click.echo("")

@cli.command()
@click.option("--dev", is_flag=True)
@click.argument("package_names", nargs=-1)
def remove(dev, package_names):
    "Remove a list of packages and their dependencies, and remove this from the requirements."
    for package_name in package_names:
        piper.remove(package_name, dev=dev)
        click.echo("")

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
@click.option("--patch", is_flag=False, help="For patch version upgrades")
@click.option("--minor", is_flag=False, help="For minor version upgrades")
@click.option("--major", is_flag=False, help="For major version upgrades")
@click.option("--latest", is_flag=False, help="For latest version upgrades")
@click.argument("package_names", nargs=-1)
def upgrade(patch, minor, major, latest, package_names):
    "Upgrade a list of packages."
    # click.echo([patch, minor, major, latest, package_names])

    for name in package_names:
        piper.upgrade(name, patch=patch, minor=minor, major=major, latest=latest)
    
@cli.command()
def clear():
    "Deletes virtualenv, requirements folder/files and piper file."
    piper.clear()

if __name__ == '__main__':
    os.chdir("..")
    # outdated()
    cli()

    # from click.testing import CliRunner
    # runner = CliRunner()
    # result = runner.invoke(cli.outdated, [])