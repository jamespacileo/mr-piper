# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import click
import os

import sys
sys.path.append("..")
from mrpiper import piper

@click.group()
def cli():
    pass

@cli.command()
@click.option("--dev", is_flag=True)
@click.argument("package_names", nargs=-1)
def add(dev, package_names):
    "Install and add a package to requirements"
    for package_name in package_names:
        piper.add(package_name, dev=dev)
        click.echo("")

@cli.command()
@click.option("--noinput", is_flag=True)
@click.argument("package_names", nargs=-1)
def remove(noinput, package_names):
    "Remove a list of packages and their dependencies, and remove this from the requirements."
    for package_name in package_names:
        piper.remove(package_name, dev=dev)
        click.echo("")

@cli.command()
@click.option("--dev", is_flag=True, help="If to install dev packages")
def install(dev):
    "Install all packages in requirement files."
    piper.install(dev=dev)

@cli.command()
@click.option("--import", "-r", "file_to_import", help="Import from existing requirements file")
@click.option("--inside", "virtualenv_location", flag_value="inside", default=True)
@click.option("--outside", "virtualenv_location", flag_value="outside")
@click.option("--py", type=click.Choice(["2", "2.7", "3", "3.3", "3.4", "3.5", "3.6"]))
@click.option("--global", "is_global", is_flag=True)
def init(file_to_import, virtualenv_location, py, is_global):
    "Initialise project with virtual environment, requirements structure and package lock."
    click.echo("Initializing project")
    piper.init()

@cli.command()
@click.option("--patch", "upgrade_level", flag_value="patch", help="For patch version upgrades")
@click.option("--minor", "upgrade_level", flag_value="minor", help="For minor version upgrades")
@click.option("--major", "upgrade_level", flag_value="major", help="For major version upgrades")
@click.option("--latest", "upgrade_level", flag_value="latest", help="For latest version upgrades")
@click.option("--all", is_flag=True, help="Upgrade all packages")
@click.option("--noinput", is_flag=True)
@click.argument("package_names", nargs=-1)
def upgrade(upgrade_level, all, noinput, package_names):
    "Upgrade a list of packages."
    # click.echo([patch, minor, major, latest, package_names])

    if all:
        piper.upgrade_all(upgrade_level)
    else:
        for name in package_names:
            piper.upgrade(name, upgrade_level)

@cli.command()
@click.option("--format", default="table", help="Output format")
@click.option("--verbose", is_flag=True)
def outdated(format, verbose):
    "Deletes virtualenv, requirements folder/files and piper file."
    piper.outdated()

@cli.command()
@click.option("--noinput", is_flag=True)
def clear(noinput):
    "Deletes virtualenv, requirements folder/files and piper file."
    piper.clear()

if __name__ == '__main__':
    # os.chdir("..")
    # outdated()
    cli()

    # from click.testing import CliRunner
    # runner = CliRunner()
    # result = runner.invoke(cli.outdated, [])
