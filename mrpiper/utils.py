import os
import hashlib
import tempfile
from __future__ import unicode_literals

import click
import delegator
from pip.req.req_file import parse_requirements, process_line
from pip.req.req_install import InstallRequirement
from piptools.resolver import Resolver
from piptools.repositories.pypi import PyPIRepository
from piptools.scripts.compile import get_pip_command
from piptools import logging

from .vendor.requirements.parser import parse as parse_requirements_alt
# from piper import which, which_pip

# Packages that should be ignored later.
IGNORED_PACKAGES = (
    'setuptools', 'pip', 'wheel', 'six', 'packaging',
    'pyparsing', 'appdirs', 'pipenv'
)

def add_line_to_requirements(filename, line):
    pass

def add_to_requirements_file(req, filename):
    # click.echo("Adding module to requirements")
    old_reqs = [r for r in parse_requirements(filename, session='')]

    if req.editable:
        install_req = InstallRequirement.from_editable(req.line.replace("-e ", ""))
    else:
        install_req = InstallRequirement.from_line(req.line)

    reqs = []
    replaced = False
    for old_req in old_reqs:
        # click.echo(old_req)
        if old_req.name.lower() == install_req.name.lower():
            replaced = True
            reqs.append(install_req)
            # click.echo(install_req)
        else:
            reqs.append(old_req)
            # click.echo(old_req)

    if not replaced:
        reqs.append(install_req)

    # requirements = []

    # click.echo("List of requirements: {0}".format(reqs))

    with open(filename + ".tmp", "w") as file:
        # click.echo(file.name)
        for package in reqs:
            # click.echo("Adding package {0}".format(package))
            if package.name not in IGNORED_PACKAGES:
                if package.link is not None:
                    package_string = (
                        '-e {0}'.format(
                            package.link
                        ) if package.editable else str(package.link)
                    )
                    # project.add_package_to_pipfile(package_string)
                    # requirements.append(package_string)
                    file.write(package_string + "\n")
                else:
                    file.write(str(package.req) + "\n")
                    # requirements.append(packa)
        file.close()
        # project.recase_pipfile()
    
    os.remove(filename)
    os.rename(filename+".tmp", filename)
    return

def add_to_requirements_lockfile(reqs, filename):
    # click.echo("Adding module to requirements")

    new_reqs = []
    for req in reqs:
        if req.editable:
            install_req = InstallRequirement.from_editable(req.line.replace("-e ", ""))
        else:
            install_req = InstallRequirement.from_line(req.line)
        new_reqs.append(install_req)

    with open(filename + ".tmp", "w") as file:
        # click.echo(file.name)
        for package in new_reqs:
            # click.echo("Adding package {0}".format(package))
            if package.name not in IGNORED_PACKAGES:
                if package.link is not None:
                    package_string = (
                        '-e {0}'.format(
                            package.link
                        ) if package.editable else str(package.link)
                    )
                    # project.add_package_to_pipfile(package_string)
                    # requirements.append(package_string)
                    file.write(package_string + "\n")
                else:
                    file.write(str(package.req) + "\n")
                    # requirements.append(packa)
        file.close()
        # project.recase_pipfile()
    
    os.remove(filename)
    os.rename(filename+".tmp", filename)
    return

def compile_requirements(input_filename, output_filename):
    delegator.run('pip-compile --output-file {1} {2}'.format("", output_filename, input_filename))


def remove_from_requirements_file(req, filename):
    # click.echo("Adding module to requirements")
    old_reqs = [r for r in parse_requirements(filename, session='')]

    if req.editable:
        install_req = InstallRequirement.from_editable(req.line.replace("-e ", ""))
    else:
        install_req = InstallRequirement.from_line(req.line)

    reqs = []
    removed = False
    for old_req in old_reqs:
        # click.echo(old_req)
        if old_req.name.lower() == install_req.name.lower():
            removed = True
            continue
        else:
            reqs.append(old_req)
    
    # requirements = []

    # click.echo("List of requirements: {0}".format(reqs))

    with open(filename + ".tmp", "w") as file:
        # click.echo(file.name)
        for package in reqs:
            # click.echo("Adding package {0}".format(package))
            if package.name not in IGNORED_PACKAGES:
                if package.link is not None:
                    package_string = (
                        '-e {0}'.format(
                            package.link
                        ) if package.editable else str(package.link)
                    )
                    # project.add_package_to_pipfile(package_string)
                    # requirements.append(package_string)
                    file.write(package_string + "\n")
                else:
                    file.write(str(package.req) + "\n")
                    # requirements.append(packa)
        file.close()
        # project.recase_pipfile()
    
    os.remove(filename)
    os.rename(filename+".tmp", filename)
    return

def get_packages_from_requirements_file(filename):
    # return [r for r in parse_requirements(filename, session='')]
    reqstr = filename.text()
    if reqstr:
        with filename.parent:
            return list(parse_requirements_alt(reqstr))
    return []

def get_package_from_requirement_file(package_name, filename):
    pkgs = get_packages_from_requirements_file(filename)
    package = next(filter(lambda x: x.name.lower() == package_name.lower(), pkgs))
    return package

def map_piper_json_to_requirements():
    pass