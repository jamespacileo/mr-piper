# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import map,filter

import os
import hashlib
import tempfile

import requests
import parse
import click
import delegator
from pip.req.req_file import parse_requirements, process_line
from pip.req.req_install import InstallRequirement
# from piptools.resolver import Resolver
# from piptools.repositories.pypi import PyPIRepository
# from piptools.scripts.compile import get_pip_command
# from piptools import logging


from .vendor.requirements.parser import parse as parse_requirements_alt
# from .piper import project
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

def shellquote(s):
    """Prepares a string for the shell (on Windows too!)"""
    return '"' + s.replace("'", "'\\''") + '"'



def python_version(path_to_python):
    if not path_to_python:
        return None

    try:
        c = delegator.run([path_to_python, '--version'], block=False)
    except Exception:
        return None
    output = c.out.strip() or c.err.strip()

    @parse.with_pattern(r'.*')
    def allow_empty(text):
        return text

    TEMPLATE = 'Python {}.{}.{:d}{:AllowEmpty}'
    parsed = parse.parse(TEMPLATE, output, dict(AllowEmpty=allow_empty))
    if parsed:
        parsed = parsed.fixed
    else:
        return None

    return u"{v[0]}.{v[1]}.{v[2]}".format(v=parsed)

def resolve_git_shortcut(git_shortcut):
    result = parse.parse("{:w}/{:w}#{:w}", git_shortcut)
    if not result:
        result = parse.parse("{:w}/{:w}", git_shortcut)
    if not result:
        return False

    username = result.fixed[0]
    project = result.fixed[1]

    git_tag = None
    if len(result.fixed) > 2:
        git_tag = result.fixed[2]


    r = requests.get("https://raw.githubusercontent.com/{0}/{1}/master/setup.py".format(username, project))
    if r.status_code == 404:
        return False

    result = parse.search("name='{}'", r.content)
    result2 = parse.search('name="{}"', r.content)
    if result:
        egg_name = result.fixed[0]
    elif result2:
        egg_name = result2.fixed[0]
    else:
        egg_name = project

    if git_tag:
        return "git+https://github.com/{0}/{1}.git@{2}#egg={3}".format(username, project, git_tag, egg_name)
    else:
        return "git+https://github.com/{0}/{1}.git#egg={2}".format(username, project, egg_name)
