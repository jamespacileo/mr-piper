# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import click_log
click_log.basic_config(logger)

import click
import os

# import sys
# sys.path.append("..")
from . import piper

@click.group()
def cli():
    pass

# @cli.command()
# @click.option("--dev", is_flag=True)
# @click.argument("package_names", nargs=-1)
# def add(dev, package_names):
#     "Install and add a package to requirements"
#     for package_name in package_names:
#         piper.add(package_name, dev=dev)
#         click.echo("")

@cli.command()
@click.option("--dev", is_flag=True)
@click.option("--editable", "-e", is_flag=True)
@click.argument("package_names", nargs=-1)
@click_log.simple_verbosity_option(logger)
def add(dev, editable, package_names):
    "Install and add a package to requirements"
    for package_name in package_names:
        piper.add(package_name, editable=editable, dev=dev)
        # click.echo("")

@cli.command()
@click.option("--noinput", is_flag=True)
@click.argument("package_names", nargs=-1)
@click_log.simple_verbosity_option(logger)
def remove(noinput, package_names):
    "Remove a list of packages and their dependencies, and remove this from the requirements."
    for package_name in package_names:
        piper.remove(package_name)
        click.echo("")

@cli.command()
@click.option("--dev", is_flag=True, help="If to install dev packages")
@click_log.simple_verbosity_option(logger)
def install(dev):
    "Install all packages in requirement files."
    piper.install(dev=dev)

@cli.command()
@click.option("--import", "-r", "file_to_import", help="Import from existing requirements file")
@click.option("--inside", "virtualenv_location", flag_value="inside", default=True, help="Place virtualenv inside the project folder")
@click.option("--outside", "virtualenv_location", flag_value="outside", help="Place virtualenv outside the project folder")
@click.option("--yes", "-y", "noinput", help="For no-input mode")
@click.option("--private", "-p", "private", help="For private libraries or applications")
@click.option("--py", type=click.Choice(["2", "2.7", "3", "3.3", "3.4", "3.5", "3.6"]), help="Which Python version should be used")
@click.option("--global", "is_global", is_flag=True, help="Use global Python")
@click_log.simple_verbosity_option(logger)
def init(file_to_import, virtualenv_location, noinput, private, py, is_global):
    "Initialise project with virtual environment, requirements structure and package lock."
    click.echo("Initializing project")
    piper.init(noinput=noinput)

@cli.command()
@click.option("--patch", "upgrade_level", flag_value="patch", help="For patch version upgrades")
@click.option("--minor", "upgrade_level", flag_value="minor", help="For minor version upgrades")
@click.option("--major", "upgrade_level", flag_value="major", help="For major version upgrades")
@click.option("--latest", "upgrade_level", flag_value="latest", help="For latest version upgrades")
@click.option("--all", is_flag=True, help="Upgrade all packages")
@click.option("--noinput", is_flag=True)
@click.argument("package_names", nargs=-1)
@click_log.simple_verbosity_option(logger)
def upgrade(upgrade_level, all, noinput, package_names):
    "Upgrade a list of packages."
    # click.echo([patch, minor, major, latest, package_names])

    if all:
        piper.upgrade_all(upgrade_level)
    else:
        for name in package_names:
            piper.upgrade(name, upgrade_level)

@cli.command()
@click.option("--format", "output_format", default="table", help="Output format")
@click.option("--all", "all_pkgs", is_flag=True, help="Show all dependencies, not just the top level ones.")
@click.option("--verbose", is_flag=True, help="Show some extra columns")
@click_log.simple_verbosity_option(logger)
def outdated(output_format, all_pkgs, verbose):
    "Deletes virtualenv, requirements folder/files and piper file."
    # logger.error("Test message")
    piper.outdated(format=output_format, all_pkgs=all_pkgs, verbose=verbose)

@cli.command()
@click.option("--noinput", is_flag=True)
def clear(noinput):
    "Deletes virtualenv, requirements folder/files and piper file."
    piper.clear()

@cli.command()
@click.argument("package_name", help="Package name you want to explain why")
@click_log.simple_verbosity_option(logger)
def why(package_name):
    "Explain why a package exists"
    piper.why(package_name)

if __name__ == '__main__':
    # os.chdir("..")
    # outdated()
    cli()

    # from click.testing import CliRunner
    # runner = CliRunner()
    # result = runner.invoke(cli.outdated, [])
