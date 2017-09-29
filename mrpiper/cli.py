# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import click_log
click_log.basic_config(logger)

import click
click.disable_unicode_literals_warning = True
import os

# import sys
# sys.path.append("..")
from . import piper

@click.group()
def cli():
    """
    \b
     _____ _
    |  __ (_)
    | |__) | _ __   ___ _ __
    |  ___/ | '_ \ / _ \ '__|
    | |   | | |_) |  __/ |
    |_|   |_| .__/ \___|_|
            | |
            |_|
    """

# @cli.command()
# @click.option("--dev", is_flag=True)
# @click.argument("package_names", nargs=-1)
# def add(dev, package_names):
#     "Install and add a package to requirements"
#     for package_name in package_names:
#         piper.add(package_name, dev=dev)
#         click.echo("")

@cli.command()
@click.option("--import", "-r", "file_to_import", help="Import from existing requirements file")
@click.option("--inside", "virtualenv_location", flag_value="inside", default=True, help="Place virtualenv inside the project folder")
@click.option("--outside", "virtualenv_location", flag_value="outside", help="Place virtualenv outside the project folder")
@click.option("--yes", "-y", "noinput", is_flag=True, help="For no-input mode")
@click.option("--private", "-p", "private", help="For private libraries or applications")
@click.option("--py", "python", help="Which Python version should be used e.g. 2.7, 3.6")
# @click.option("--py", type=click.Choice(["2", "2.7", "3", "3.3", "3.4", "3.5", "3.6"]), help="Which Python version should be used")
@click.option("--global", "is_global", is_flag=True, help="Use global Python")
@click.option("--installable", "installable", is_flag=True, help="Use installable Python")
@click_log.simple_verbosity_option(logger)
def init(file_to_import, virtualenv_location, noinput, private, python, is_global, installable):
    """
    \b
    Initialises the project with:
    - a Piper project file (piper.json)
    - a Piper lock file (piper.lock)
    - legacy PIP requirements (base.txt, base-locked.txt, dev.txt, dev-locked.txt)
    - (optional) a pre-configured setup.py

    Examples:

    > piper init
    > piper init --py 3.6
    > piper init -y

    """
    piper.init(noinput=noinput, python=python, virtualenv_location=virtualenv_location, installable=installable)



@cli.command()
@click.option("--dev", is_flag=True)
@click.option("--editable", "-e", is_flag=True)
@click.argument("package_names", nargs=-1)
@click_log.simple_verbosity_option(logger)
def add(dev, editable, package_names):
    """
    Install and add a package to requirements

    \b
    Examples:
    $ piper add django
    $ piper add pytest --dev
    $ piper add -e requests/requests
    """
    for package_name in package_names:
        piper.add(package_name, editable=editable, dev=dev)
        # click.echo("")

@cli.command()
@click.option("--noinput", is_flag=True)
@click.argument("package_names", nargs=-1)
@click_log.simple_verbosity_option(logger)
def remove(noinput, package_names):
    """
    Remove a list of packages and their dependencies, and remove this from the requirements.

    \b
    Example:
    $ piper remove django --noinput
    """
    for package_name in package_names:
        piper.remove(package_name)
        click.echo("")

@cli.command()
@click.option("--dev", is_flag=True, help="If to install dev packages")
@click.option("--cache", "cache_url", default=None, help="Cache url to grab packages from")
@click.option("--hashes", "require_hashes", is_flag=True, help="Should install check the hashes")
@click_log.simple_verbosity_option(logger)
def install(dev, cache_url, require_hashes):
    """
    Install all packages in requirement files.

    \b
    Examples:
    $ piper install
    $ piper install --dev
    $ piper install --hashes
    """
    piper.install(dev=dev, cache_url=cache_url, require_hashes=require_hashes)


@cli.command()
@click.option("--patch", "upgrade_level", flag_value="patch", help="For patch version upgrades")
@click.option("--minor", "upgrade_level", flag_value="minor", help="For minor version upgrades")
@click.option("--major", "upgrade_level", flag_value="major", help="For major version upgrades")
@click.option("--latest", "upgrade_level", flag_value="latest", help="For latest version upgrades")
@click.option("--all", is_flag=True, help="Upgrade all packages")
@click.option("--yes", "-y", "noinput", is_flag=True)
@click.argument("package_names", nargs=-1)
@click_log.simple_verbosity_option(logger)
def upgrade(upgrade_level, all, noinput, package_names):
    """
    Upgrade a list of packages.

    \b
    Examples:
    $ piper upgrade django --latest
    $ piper upgrade requests --patch
    $ piper upgrade --all --yes
    """
    # click.echo([patch, minor, major, latest, package_names])

    if all:
        piper.upgrade_all(upgrade_level, noinput=noinput)
    else:
        for name in package_names:
            piper.upgrade(name, upgrade_level, noinput=noinput)

@cli.command()
# @click.option("--format", "output_format", default="table", type=click.Choice(["table", "json"]), help="Output format")
@click.option("--table", "output_format", flag_value="table", default=True, help="Format output as a table")
@click.option("--json", "-j", "output_format",flag_value="json", help="Format output as JSON")
@click.option("--all", "all_pkgs", is_flag=True, help="Show all dependencies, not just the top level ones.")
@click.option("--verbose", is_flag=True, help="Show some extra columns")
@click_log.simple_verbosity_option(logger)
def outdated(output_format, all_pkgs, verbose):
    """
    Deletes virtualenv, requirements folder/files and piper file.

    \b
    Example:
    $ piper outdated --all --json

    """
    # logger.error("Test message")
    # logger.debug("{0} {1} {2}".format(output_format, all_pkgs, verbose))
    piper.outdated(output_format=output_format, all_pkgs=all_pkgs, verbose=verbose)

@cli.command()
@click.option("--noinput", is_flag=True)
def wipe(noinput):
    "Wipe virtualenv, requirements folder/files and piper files."
    piper.wipe(noinput=noinput)

@cli.command()
@click.argument("package_name") #, help="Package name you want to explain why")
@click_log.simple_verbosity_option(logger)
def why(package_name):
    """
    Explain why a package exists

    \b
    Example:
    $ piper why django

    """
    piper.why(package_name)


@cli.command()
@click_log.simple_verbosity_option(logger)
def list():
    """
    List all installed packages

    \b
    Example:
    $ piper list

    """
    piper.dependency_list()


@cli.command()
@click.option("--yes", "-y", "noinput", is_flag=True)
@click_log.simple_verbosity_option(logger)
def version(noinput):
    """
    Get and set project version

    \b
    Example:
    $ piper version -y

    """
    piper.version(noinput)

@cli.command()
@click.argument("package_name", nargs=1)
@click_log.simple_verbosity_option(logger)
def info(package_name):
    """
    info all installed packages

    \b
    Example:
    $ piper info django

    """
    piper.info(package_name)

@cli.command()
@click_log.simple_verbosity_option(logger)
def activate():
    """
    Echo the virtualenv activation commandline

    \b
    Example:
    $ piper activate
    """
    piper.activate()

@cli.command()
@click.option("--output", "-o", "output_dir", default="./piper_cache")
@click.option("--dev", "dev", is_flag=True)
@click_log.simple_verbosity_option(logger)
def cache(output_dir, dev=False):
    """
    Cache your installed packages

    \b
    Example:
    $ piper cache -o /path/to/cache
    """
    piper.cache(output_dir, dev)

@cli.command()
@click_log.simple_verbosity_option(logger)
def fix():
    "Fix"
    piper.fix()

@cli.command()
@click_log.simple_verbosity_option(logger)
def hash():
    """
    Gather dependency hashes

    \b
    Example:
    $ piper hash
    """
    piper.hash()

@cli.command()
@click.argument("name")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click_log.simple_verbosity_option(logger)
def run(name, args):
    """
    Run a list of scripts sequentially

    \b
    Example:
    $ piper run build_publish
    """
    piper.run(name, args)


@cli.command()
@click_log.simple_verbosity_option(logger)
def integrity():
    """
    Run an integrity check and fix any discrepancies in the lock and requirement files

    \b
    Example:
    $ piper integrity
    """
    piper.check_integrity()

@cli.command()
@click_log.simple_verbosity_option(logger)
def shell():
    """
    Run a shell within the virtualenv

    \b
    Example:
    $ piper shell
    """
    piper.shell()

# @cli.command()
# @click.argument('timeit_args', nargs=-1, type=click.UNPROCESSED)
# def python(args):
#     piper.run_bin("python", args)

if __name__ == '__main__':
    # os.chdir("..")
    # outdated()
    cli()

    # from click.testing import CliRunner
    # runner = CliRunner()
    # result = runner.invoke(cli.outdated, [])
