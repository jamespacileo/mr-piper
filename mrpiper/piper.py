# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import map, filter, zip

import contextlib
import codecs
import json
import os
import sys
import distutils.spawn
import shutil
import signal
import tempfile
import pdb
import crayons
import time
import logging
logger = logging.getLogger("mrpiper.cli")


import tabulate
from path import Path
import parse
import click
import delegator
import semantic_version
import click_spinner
import emoji

from pkg_resources import Requirement as Req
from pkg_resources import RequirementParseError
from pip.req.req_file import parse_requirements, process_line

from .vendor.requirements.requirement import Requirement
from .vendor.requirements.parser import parse as parse_requirements
from .vendor import pipdeptree

from .overrides import parse as special_parse_requirements

# import pipfile

from .utils import add_to_requirements_file, compile_requirements, add_to_requirements_lockfile,  \
    remove_from_requirements_file, get_packages_from_requirements_file, get_package_from_requirement_file, \
    shellquote, python_version, IGNORED_PACKAGES, resolve_git_shortcut
from . import overrides
from .project import PythonProject
from . import pyenv_utils

project = PythonProject()


def system_which(command, mult=False):
    """Emulates the system's which. Returns None is not found."""

    _which = 'which -a' if not os.name == 'nt' else 'where'

    c = delegator.run('{0} {1}'.format(_which, command))
    try:
        # Which Not found...
        if c.return_code == 127:
            click.echo(
                '{}: the {} system utility is required for Pipenv to find Python installations properly.'
                '\n  Please install it.'.format(
                    crayons.red('Warning', bold=True),
                    crayons.red(_which)
                ), err=True
            )
        assert c.return_code == 0
    except AssertionError:
        return None if not mult else []

    result = c.out.strip() or c.err.strip()

    if mult:
        return result.split('\n')
    else:
        return result.split('\n')[0]

def find_a_system_python(python):
    """Finds a system python, given a version (e.g. 2.7 / 3.6.2), or a full path."""
    if python.startswith('py'):
        return system_which(python)
    elif os.path.isabs(python):
        return python
    else:
        possibilities = reversed([
            'python',
            'python{0}'.format(python[0]),
            'python{0}{1}'.format(python[0], python[2]),
            'python{0}.{1}'.format(python[0], python[2]),
            'python{0}.{1}m'.format(python[0], python[2])
        ])

        for possibility in possibilities:
            # Windows compatibility.
            if os.name == 'nt':
                possibility = '{0}.exe'.format(possibility)

            versions = []
            pythons = system_which(possibility, mult=True)

            for p in pythons:
                versions.append(python_version(p))

            for i, version in enumerate(versions):
                if python in (version or ''):
                    return pythons[i]

def which(command):
    if os.name == 'nt':
        if command.endswith('.py'):
            return os.sep.join([project.virtualenv_dir] + ['Scripts\{0}'.format(command)])
        return os.sep.join([project.virtualenv_dir] + ['Scripts\{0}.exe'.format(command)])
    return os.sep.join([project.virtualenv_dir] + ['bin/{0}'.format(command)])


def which_pip(allow_global=False):
    """Returns the location of virtualenv-installed pip."""
    if allow_global:
        return distutils.spawn.find_executable('pip')

    return which('pip')

def get_dependency_tree():
    vendor_path = Path(pipdeptree.__file__)
    command = "{0} {1} --json".format(which("python"), shellquote(vendor_path))
    c = delegator.run(command)
    if c.return_code != 0:
        return {}
    return json.loads(c.out)

def pip_wheel(output_dir, requirements):
    pip_command = "{0} wheel --wheel-dir={1} -r {2}".format(
        which_pip(),
        shellquote(output_dir),
        shellquote(requirements)
    )
    c = delegator.run(pip_command)
    return c
    # return c.return_code == 0

def pip_freeze():
    # temp = tempfile.TemporaryFile()
    # pip_command = '{0} freeze > {1}'.format(which_pip(), temp.name)
    pip_command = '{0} freeze'.format(which_pip())
    c = delegator.run(pip_command)

    # click.echo(pip_command)
    # click.echo(c2.out)

    frozen_reqs = c.out
    frozen_reqs = [req for req in parse_requirements(frozen_reqs)]

    # click.echo(frozen_reqs)
    return frozen_reqs

    # if c.return_code == 0:
    #     return False

    # # Return the result of the first one that runs ok, or the last one that didn't work.
    # return c

def pip_install_list(packages, allow_global=False, cache_url=None, require_hashes=False):

    hashes_string = "--require-hashes" if require_hashes else ""

    if cache_url:
        # --no-cache-dir
        pip_command = "{0} install {1} --no-index --no-deps --find-links={2} {3}".format(
            which_pip(),
            hashes_string,
            shellquote(cache_url),
            " ".join(packages)
        )
    else:
        pip_command = "{0} install {1} --no-deps {2}".format(
            which_pip(),
            hashes_string,
            " ".join(packages)
        )
    logger.debug(pip_command)
    c = delegator.run(pip_command)
    return c

    # pip_commands = []
    # for package in packages:
    #     pip_command = "{0} install --no-deps {1}".format(
    #         which_pip(),
    #         package
    #     )
    #     pip_commands.append(pip_command)


    # delegated_commands = []
    # for cmd in pip_commands:
    #     click.echo(cmd)
    #     c = delegator.run(cmd, block=True)
    #     delegated_commands.append(c)

    # map(lambda x: x.block(), delegated_commands)
    # return delegated_commands

def pip_install_from_cache(
    cache_dir, requirements_file, require_hashes=False
):
    pip_command = "{0} install --no-index --find-links={1} -r {2}".format(
        which_pip(),
        shellquote(cache_dir),
        shellquote(requirements_file)
    )
    c = delegator.run(pip_command)
    return c


def pip_install(
    package_name=None, r=None, allow_global=False, editable=False, no_deps=False, block=True, upgrade=False
):

    # Create files for hash mode.
    # if (not ignore_hashes) and (r is None):
    #     r = tempfile.mkstemp(prefix='pipenv-', suffix='-requirement.txt')[1]
    #     with open(r, 'w') as f:
    #         f.write(package_name)

    if r:
        install_reqs = ' -r {0}'.format(r)
    elif package_name.startswith('-e '):
        install_reqs = ' -e "{0}"'.format(package_name.split('-e ')[1])
    else:
        install_reqs = ' "{0}"'.format(package_name)

    if editable:
        if package_name.startswith('-e '):
            package_name = package_name.split('-e ')[1]
        install_reqs = ' -e "{0}"'.format(package_name)

    no_deps = '--no-deps' if no_deps else ''
    upgrade_str = '-U' if upgrade else ''

    pip_command = '"{0}" install {2} {1} {3} --exists-action w'.format(
        which_pip(allow_global=allow_global),
        install_reqs,
        no_deps,
        upgrade_str
    )
    logger.debug(pip_command)
    c = delegator.run(pip_command, block=block)

    # if c.return_code == 0:
    #     return c

    # Return the result of the first one that runs ok, or the last one that didn't work.
    return c

def pip_uninstall(packages):
    pip_command = "{0} uninstall --yes {1}".format(which_pip(), " ".join(packages))
    logger.debug(pip_command)
    c = delegator.run(pip_command)
    return c

def pip_show(package_name):
    pip_command = "{0} show {1}".format(which_pip(), package_name)
    c = delegator.run(pip_command)
    return c.out

def pip_versions(package_name):
    pip_command = "{0} install {1}==0.xx".format(which_pip(), package_name)
    c = delegator.run(pip_command)
    no_matching = "No matching distribution found for mrpiper" in c.err
    if no_matching:
        return False

    main_result = parse.search("from versions: {})", c.err)
    # click.echo([package_name, c.err])
    # click.echo([package_name, result.fixed[0], [item for item in parse.findall(" {:S},", result.fixed[0] + ",")]])
    results = [result.fixed[0] for result in parse.findall(" {:S},", main_result.fixed[0] + ",")]
    # last_result = [result.fixed[0] for result in parse.findall(" {:w})", result.fixed[0])]
    # click.echo(results)
    # logger.error("No results? {0} \nMAIN: {1} \nRESULTS: {2}".format(c.err, main_result.fixed[0], type(results)))
    if not results:
        return []

    return results

def pip_list():
    pip_command = "{0} list --format=json".format(which_pip())
    logger.debug(pip_command)
    c = delegator.run(pip_command)
    return json.loads(c.out)



def pip_outdated():
    pip_command = "{0} list -o --format columns".format(which_pip())
    logger.debug(pip_command)
    c = delegator.run(pip_command)
    return c


def check_before_running(func):
    def wrapper(*args, **kwargs):

        if not project.has_virtualenv:
            click.secho("There is no virtualenv setup for this project, please use " + crayons.yellow("piper init"), fg="red")
            sys.exit(1)
        if not project.has_piper_file:
            click.secho("There is no project piper file for this project, please use " + crayons.yellow("piper init"), fg="red")
            sys.exit(1)
        if not project.has_piper_lock:
            click.secho("There is no project lock file for this project, please use " + crayons.yellow("piper init"), fg="red")
            sys.exit(1)
        # if not project.has_piper_file:
        #     click.secho("There is no project piper file for this project, please use " + crayons.yellow("piper init"), fg="red")
        return func(*args, **kwargs)
    return wrapper

def init(noinput=False, private=False, python=None, virtualenv_location="inside", installable=False):
    click.echo("🔨  Initializing project")
    # create requirements structure
    # create virtualenv
    if python:
        found_python = find_a_system_python(python)
        if not found_python:
            click.echo(
                crayons.red("Couldn't find the python executable for: ") + crayons.yellow(python)
            )
            sys.exit(1)
        else:
            python = found_python
            click.echo(
                "found python version" + python
            )

    if noinput:
        init_data = {
            "private": private
        }
    else:
        init_data = {}
    project.setup(noinput=noinput, init_data=init_data, python=python, virtualenv_location=virtualenv_location, installable=installable)

    click.echo(
        crayons.green(emoji.emojize("\n:sparkles:  Initialization complete", use_aliases=True))
    )

@check_before_running
def add(package_line, editable=False, dev=False, dont_install=False):
    # create requirements
    # init()
    click.secho("[1/2] 🔍  Locating package {}...".format(crayons.yellow(package_line), fg="yellow"))
    # if editable:
    #     click.secho("Installing {0} in editable mode...".format(crayons.yellow(package_line)))
    # else:
    #     click.secho("Installing {0}...".format(crayons.yellow(package_line)))

    could_be_github = parse.parse("{:w}/{:w}#{:w}", package_line) or parse.parse("{:w}/{:w}", package_line)
    if could_be_github:
        git_url = resolve_git_shortcut(package_line)
        click.secho("{0} resolved as {1}".format(
            crayons.yellow(package_line),
            crayons.green(git_url)
        ))
        package_line = git_url

    # req = Req.parse(package_line)
    # logger.debug("{}".format(req.__dict__))

    # if editable:
    #     req = Requirement.parse_editable(package_line)
    # else:
    #     req = Requirement.parse_line(package_line)

    if editable:
        req = overrides.SmartRequirement.from_editable(package_line)
    else:
        req = overrides.SmartRequirement.from_line(package_line)

    # click.echo(req.__dict__)

    logger.debug("Requirement parsed: {}".format(req.__dict__))

    has_specs = len(req.specs) > 0
    is_vcs = req.vcs
    is_local_file = req.local_file
    is_editable = req.editable

    if is_vcs:
        is_editable = True

    # if is_vcs and (not is_editable):
    #     # print("Make sure ")
    #     req.editable = True
    #     package_line = "-e {0}".format(package_line)

    if is_vcs and (not req.name):
        click.secho("Make sure to add #egg=<name> to your url", fg="red")
        sys.exit(1)

    click.secho("[2/2] 🔨  Installing {}...".format(crayons.yellow(package_line), fg="yellow"))
    with click_spinner.spinner():
        c = pip_install(package_line, editable=is_editable, allow_global=False, block=True)

    # counter = 0
    # with click.progressbar(length=10) as bar:
    #     while time.sleep(0.5):
    #         counter = max(counter + 1, 10)
    #         bar.update(counter)
    #         if not (c.blocking == None):
    #             click.echo("Return code is:" + c.return_code)
    #             bar.update(10)
    #             break
    # result = parse.search("Successfully installed {} \n", c.out)

    if not (c.return_code == 0):
        click.secho(c.err, fg="red")
        click.echo(
            crayons.red("Failed to install ") + crayons.yellow(req.name) + crayons.red(" ✗")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )
        sys.exit()
    else:
        click.secho(c.out.rstrip(), fg="blue")

        click.echo(
            crayons.green("Package ") + crayons.yellow(req.name) + crayons.green(" installed ✓")
            # crayons.green("Package {0} installed ✓".format(crayons.yellow(req.name)))
            )

    result = parse.search("Successfully installed {}\n", c.out)
    succesfully_installed = result.fixed[0].split() if result else []
    succesfully_installed = [item.rsplit('-', 1)[0] for item in succesfully_installed]
    existing_packages = [result.fixed[0] for result in parse.findall("Requirement already satisfied: {} in", c.out)]

    all_pkgs = succesfully_installed + existing_packages
    all_pkgs = [Req.parse(pkg).unsafe_name for pkg in all_pkgs]

    # click.secho("Locking requirements...")

    frozen_deps = pip_freeze()
    frozen_dep = next(filter(lambda x: x.name.lower() == req.name.lower(), frozen_deps), None)
    project.update_frozen_dependencies_in_piper_lock(frozen_deps)

    dependency = {
        "name": frozen_dep.name,
        # "line": req.line if ((not req.vcs) and (not req.local_file) and req.specs) else frozen_dep.line.replace("==",">="),
        "line": frozen_dep.line.replace("==",">="),
        "specs": frozen_dep.specs,
        "dependencies": [pkg for pkg in all_pkgs if not (pkg == frozen_dep.name)]
    }
    project.add_dependency_to_piper_lock(dependency, dev=dev)
    project.update_requirement_files_from_piper_lock()

    click.secho("Requirements locked ✓", fg="green")

    # click.echo("All pkgs: {}".format(all_pkgs))

    # click.secho("Updating requirement files...")

    # if (not req.vcs) and (not req.local_file) and req.specs:
    #     add_to_requirements_file(req, os.path.join(".", "requirements", "dev.txt"))
    # else:
    #     add_to_requirements_file(frozen_dep, os.path.join(".", "requirements", "dev.txt"))
    # add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

    click.secho("Requirements updated ✓", fg="green")
    # compile_requirements(os.path.join(".", "requirements", "base.txt"), os.path.join(".", "requirements", "base-locked.txt"))

    # print(req.__dict__)

    click.echo(
        crayons.green(emoji.emojize("\n:sparkles:  Adding package complete", use_aliases=True))
    )


@check_before_running
def find_removable_dependencies(package_name):
    pass

@check_before_running
def remove(package_line, dev=False):
    req = Requirement.parse(package_line)
    logger.debug(req.__dict__)
    logger.debug(package_line)

    click.secho("[1/2] 🔍  Locating package {}...".format(crayons.yellow(req.name), fg="yellow"))
    click.secho("[1/2] 🗑️  Removing package {}...".format(crayons.yellow(req.name), fg="yellow"))
    # click.secho("Removing package {0}...".format(crayons.yellow(req.name)) )

    with click_spinner.spinner():
        removable_packages = project.find_removable_dependencies(req.name)
        if removable_packages:
            removable_packages.append(req.name)
            c = pip_uninstall(removable_packages)
        else:
            c = pip_uninstall([req.name])

    if not (c.return_code == 0):
        click.secho(c.err, fg="red")
        click.echo(
            crayons.red("Failed to remove ") + crayons.yellow(req.name) + crayons.red(" ✗")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )
        sys.exit()
    else:
        click.secho(c.out.rstrip(), fg="blue")
    click.echo(
        crayons.green("Package ") + crayons.yellow(req.name) + crayons.green(" removed ✓")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )

    # click.secho("Locking packages...")
    frozen_deps = pip_freeze()
    project.update_frozen_dependencies_in_piper_lock(frozen_deps)
    project.remove_dependency_to_piper_lock(req.name)
    click.secho("Packaged locked ✓", fg="green")

    project.update_requirement_files_from_piper_lock()

    # add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

    # click.secho("Updating requirement files...")
    # remove_from_requirements_file(req, os.path.join(".", "requirements", "base.txt"))
    click.secho("Requirement files updated ✓", fg="green")

    click.echo(
        crayons.green(emoji.emojize("\n:sparkles:  Package removal complete", use_aliases=True))
    )

# @check_before_running
def install(dev=False, force_lockfile=False, cache_url=False, require_hashes=False):
    # should run project setup

    virtualenv_exists = project.virtualenv_dir.exists()
    piper_lock_exists = project.piper_lock_dir.exists()
    piper_file_exists = project.piper_file_dir.exists()
    dev_locked_txt_exists = project.requirements_file("dev-locked.txt").exists()
    base_locked_txt_exists = project.requirements_file("base-locked.txt").exists()
    dev_txt_exists = project.requirements_file("dev.txt").exists()
    base_txt_exists = project.requirements_file("base.txt").exists()

    project.setup(noinput=True)

    # first choice piper.json
    # second choice requirements

    packages = None

    # First look for locks
    # Otherwise use plain

    which_requirements_file = None
    which_packages = None

    if dev:
        if piper_lock_exists:
            project.update_requirement_files_from_piper_lock()
            which_requirements_file = project.requirements_file("dev-locked.txt")
        elif project.requirements_file("dev-locked.txt").exists():
            which_requirements_file = project.requirements_file("dev-locked.txt")
        elif piper_file_exists:
            if require_hashes:
                click.secho("Error: no lock file with hashes available.")
                sys.exit(1)
            which_packages = [x[1] for x in project.piper_file["dev_dependencies"].items()]
        elif project.requirements_file("dev.txt").exists():
            which_requirements_file = project.requirements_file("dev.txt")
        else:
            click.secho("Error: no requirement files available. Please use " + crayons.yellow("piper init"))
            sys.exit(1)
    else:
        if piper_lock_exists:
            project.update_requirement_files_from_piper_lock()
            which_requirements_file = project.requirements_file("base-locked.txt")
        elif project.requirements_file("base-locked.txt").exists():
            which_requirements_file = project.requirements_file("base-locked.txt")
        elif piper_file_exists:
            if require_hashes:
                click.secho("Error: no lock file with hashes available.")
                sys.exit(1)
            which_packages = [x[1] for x in project.piper_file["dependencies"].items()]
        elif project.requirements_file("base.txt").exists():
            which_requirements_file = project.requirements_file("base.txt")
        else:
            click.secho("Error: no requirement files available. Please use " + crayons.yellow("piper init"))
            sys.exit(1)

    # if piper_lock_exists:
    #     click.echo("Installing from the piper lock file")
    #     # packages = [item[1]["line"] for item in project.piper_lock["frozen_deps"].items()] #TODO: separate base and dev
    #     project.update_requirement_files_from_piper_lock()
    # else:
    #     click.secho("Piper lock doesn't exist. Using next best option...", fg="yellow")

    # if piper_file_exists and (packages == None):
    #     click.echo("Installing from the piper file piper.json")
    #     packages = [x[1] for x in project.piper_file["dependencies"].items()]
    #     if dev:
    #         packages += [x[1] for x in project.piper_file["dev_dependencies"].items()]

    # elif (packages == None):
    #     click.secho("No piper.json file. Using next best option...", fg="yellow")

    # if dev:
    #     if dev_locked_txt_exists and (packages == None):
    #         click.echo("Installing from requirements/dev-locked.txt")
    #         packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("dev-locked.txt"))]
    #     if dev_txt_exists and (packages == None):
    #         click.echo("Installing from requirements/dev.txt")
    #         packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("dev.txt"))]

    # if base_locked_txt_exists and (packages == None):
    #     click.echo("Installing from requirements/base-locked.txt")
    #     packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("base-locked.txt"))]
    # if base_txt_exists and (packages == None):
    #     click.echo("Installing from requirements/base.txt")
    #     packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("base.txt"))]

    # if packages == []:
    #     click.secho("No installable packages found", fg="red")
    #     sys.exit(0)

    # if packages == None:
    #     click.echo(
    #         crayons.red("No available files to install packages from. Please run ") + crayons.yellow("piper init")
    #         )
    #     sys.exit()

    # if dev:
    #     packages = get_packages_from_requirements_file(project.requirements_file("dev-locked.txt"))
    # else:
    #     packages = get_packages_from_requirements_file(project.requirements_file("base-locked.txt"))
    if packages:
        c = pip_install_list(packages, cache_url=cache_url, require_hashes=require_hashes)
    elif which_requirements_file:
        c = pip_install_list(["-r", which_requirements_file.abspath()], cache_url=cache_url, require_hashes=require_hashes)

    click.secho(c.out, fg="blue")
    if c.return_code != 0:
        click.secho(c.err, fg="red")
        sys.exit(0)

    tree = get_dependency_tree()

    if piper_lock_exists:
        pass
    elif piper_file_exists:
        project.update_piper_lock_from_piper_file_and_tree(tree)
        frozen_deps = pip_freeze()
        # frozen_dep = next(filter(lambda x: x.name.lower() == req.name.lower(), frozen_deps), None)
        project.update_frozen_dependencies_in_piper_lock(frozen_deps)
    else:
        # for node in tree:
        #     if node["package"]["package_name"].lower() in packages:
        #         project.add_dependency_to_piper_lock({
        #             "dependencies": [dep["package_name"] for dep in node["dependencies"]],
        #             "line":
        #         })

        if which_requirements_file:
            packages = [_item.line for _item in special_parse_requirements("-r " + which_requirements_file)]
        else:
            packages = which_packages

        for package_line in packages:
            editable = False
            if package_line.startswith("-e "):
                editable = True
                package_line.replace("-e ","")

            if editable:
                req = overrides.SmartRequirement.from_editable(package_line)
            else:
                req = overrides.SmartRequirement.from_line(package_line)

            found = [node["dependencies"] for node in tree if (node["package"]["package_name"].lower() == req.name.lower())]
            if not found:
                continue

            found = found[0]
            dependency = {
                "name": req.name,
                "line": req.line,
                "dependencies": [item["package_name"].lower() for item in found]
            }
            project.add_dependency_to_piper_lock(dependency, dev=False)



    # cmds = pip_install_list(packages)
    # for cmd in cmds:
    #     click.echo(cmd.out + cmd.err)
    click.secho("Install completed ✓", fg="green")

    click.echo(
        crayons.green(emoji.emojize("\n:sparkles:  Install complete", use_aliases=True))
    )

@check_before_running
def outdated(all_pkgs=False, verbose=False, output_format="table"):
    # format can be table, json

    # logger.error("test error 2")

    if not (output_format == "json"):
        click.secho("[1/2] 🔍  Fetching dependency versions...", fg="yellow")
        # click.echo("Fetching outdated packages...")
    # c = pip_outdated()
    # click.echo([c.return_code, c.out, c.err])

    lock = project.piper_lock
    all_deps = [_item for _item in map(lambda x: x[1], lock["frozen_deps"].items())]

    mainDepKeys = [_i for _i in lock["dependencies"]]
    devDepKeys = [_i for _i in lock["dev_dependencies"]]
    allKeys = mainDepKeys + devDepKeys
    prime_deps = [_item for _item in filter(lambda x: x["name"].lower() in allKeys, all_deps)]

    which_deps = all_deps if all_pkgs else prime_deps

    logger.debug("which deps {0} {1} {2}".format(len(all_deps), len(prime_deps), len(which_deps)))

    outdated_map = []

    local_version_list = pip_list()

    with click_spinner.spinner():
        for index, dep in enumerate(which_deps):
            # logger.debug("index:{}".format(index))
            # logger.debug("checking versions for {}".format(dep["name"]))
            found_versions = pip_versions(dep["name"])
            # logger.debug("found versions {}".format(found_versions))
            if found_versions == False:
                # TODO: Address failure to find versions for package
                logger.debug("Couldn't find versions for {}".format(dep["name"]))
                continue
            # versions = list(found_versions)
            # versions = [item for item in found_versions]
            if not found_versions:
                logger.debug("Possible problem please investigate dep:{0} name:{1} versions:{2}".format(dep, dep["name"], found_versions))
                continue
            found_versions.reverse()

            try:
                logger.debug(dep)
                if dep["vcs"] != None:
                    current_version = next(filter(lambda x: (x["name"].lower() == dep["name"].lower()), local_version_list))#["version"]# + " ({})".format(dep["vcs"])
                else:
                    current_version = overrides.Version.coerce(dep["specs"][0][1], partial=True)

                # logger.debug("Coerce example: {0} {1}".format(overrides.Version.coerce(found_versions[0]), next(map(lambda x: overrides.Version.coerce(x, partial=True), found_versions))))

                coerced_versions = [_item for _item in map(lambda x: overrides.Version.coerce(x, partial=True), found_versions)]
                # logger.debug("Coerced list {}".format(coerced_versions))
                # version_mapping = map(lambda index, x: (x.__str__(), found_versions[index] ), enumerate(coerced_versions))
                # logger.debug("versions {0} {1}".format(coerced_versions, version_mapping))

                if dep["specifier"]:
                    spec_line = ",".join(["".join(x) for x in dep["specs"]])
                    spec = overrides.Spec(spec_line)
                    # spec = next(map(lambda x: semantic_version.Spec("".join(x) ), dep["specs"]))
                else:
                    spec = overrides.Spec(">={}".format(current_version))

                # click.echo("{} {} {}".format(versions, spec, upgrade_specifier))
                valid_versions = [_item for _item in spec.filter(coerced_versions)]
                wanted_version = spec.select(valid_versions).original_version
                patch_version = semantic_version.Spec("~={}".format(current_version.major, current_version.minor, current_version.patch)).select(valid_versions).original_version
                minor_version = semantic_version.Spec("~={}".format(current_version.major, current_version.minor, current_version.patch)).select(valid_versions).original_version
                current_version = current_version.original_version

                if output_format == "table":
                    if wanted_version != current_version:
                        wanted_version = crayons.yellow(wanted_version)
                    if patch_version != current_version:
                        patch_version = crayons.yellow(patch_version)
                    if minor_version != current_version:
                        minor_version = crayons.yellow(minor_version)

            except ValueError as err:
                logger.debug("ValueError for {0} with {1}".format(dep["name"], err))
                if dep["vcs"] != None:
                    current_version = next(filter(lambda x: (x["name"].lower() == dep["name"].lower()), local_version_list))["version"]# + " ({})".format(dep["vcs"])
                else:
                    current_version = overrides.Version.coerce(dep["specs"][0][1], partial=True).original_version

                # click.echo(err)
                wanted_version = "//"
                patch_version = "//"
                minor_version = "//"

            latest_version = found_versions[0]
            if (output_format == "table") and (latest_version != current_version):
                latest_version = crayons.yellow(latest_version)

            # outdated_map.append({
            #     'name': dep["name"],
            #     'current': current_version,
            #     'wanted': wanted_version.__str__(),
            #     'latest': latest_version.__str__(),
            # })

            if dep["vcs"]:
                current_version = "{0} ({1})".format(current_version, dep["vcs"])

            if verbose:
                outdated_map.append([
                    dep["name"],
                    current_version,
                    wanted_version,
                    patch_version,
                    minor_version,
                    latest_version,
                ])
            else:
                outdated_map.append([
                    dep["name"],
                    current_version,
                    wanted_version,
                    latest_version,
                ])

    if not (output_format == "json"):
        click.secho("[2/2] 🔨  Normalising results...", fg="yellow")

    if output_format == "table":
        if verbose:
            click.echo(tabulate.tabulate(outdated_map, headers=["Name", "Current", "Wanted", "Patch", "Minor", "Latest"]))
        else:
            click.echo(tabulate.tabulate(outdated_map, headers=["Name", "Current", "Wanted", "Latest"]))
    else:
        headers = headers=["Name", "Current", "Wanted", "Patch", "Minor", "Latest"] if verbose else ["Name", "Current", "Wanted", "Latest"]
        output = [dict(zip(headers, item)) for item in outdated_map]
        logger.debug(output)
        click.echo(json.dumps(output, indent=4))
    # frozen_reqs = [req for req in parse_requirements(os.path.join(".", "requirements", "base-locked.txt"))]

    # versions = pip_versions("django")
    # click.echo(versions)



@check_before_running
def upgrade(package_line, upgrade_level="latest", noinput=False):
    # get current version

    req = Requirement.parse(package_line)
    click.secho("Installing {0}...".format(crayons.yellow(req.name)))

    logger.debug(req.__dict__)

    is_flag_latest = upgrade_level in ["major", "latest"]

    dep_type = project.detect_type_of_dependency(req.name)
    dev = dep_type == "dev"
    if dep_type == "dev":
        local_package = get_package_from_requirement_file(req.name, project.requirements_file("dev-locked.txt"))
    else:
        local_package = get_package_from_requirement_file(req.name, project.requirements_file("base-locked.txt"))

    if not local_package:
        click.secho("Package is not installed", fg="red")
        sys.exit(1)

    if local_package.vcs or local_package.editable:
        click.secho("Skipped. Editable sources not supported at the moment")
        return

    if (not is_flag_latest) and (local_package.vcs):
        click.secho("Can't do patch or minor upgrade for packages installed via version control. Please use --latest")

    from pip._vendor.distlib.version import NormalizedVersion
    local_version = local_package.specs[0][1]
    norm = NormalizedVersion(local_version)
    clause = [str(item) for item in norm._release_clause]
    if len(clause) < 2:
        clause.extend(["0", "0"])
    elif len(clause) < 3:
        clause.append("0")

    upgrade_specifier = ""
    if upgrade_level == "patch":
        upgrade_specifier = "~={0}".format(".".join(clause))
    elif upgrade_level == "minor":
        del clause[2]
        upgrade_specifier = "~={0}".format(".".join(clause))

    if not noinput:
        original_versions = pip_versions(local_package.name)
        original_versions.reverse()
        if not original_versions:
            logger.error("Possible error {}".format(original_versions))

        # coerced_versions = [_item for _item in map(lambda x: overrides.Version.coerce(x, partial=True), original_versions)]
        # # versions = list(map(lambda x: overrides.Version.coerce(x, partial=True), original_versions))
        # if not coerced_versions:
        #     logger.error("Possible error 2 {0} {1}".format(original_versions, coerced_versions))
        # coerced_versions.reverse()


        try:
            logger.debug("req:{}".format(req.__dict__))
            # current_version = overrides.Version.coerce(req.specs[0][1], partial=True)
            try:
                dep = project.piper_lock["frozen_deps"][req.name.lower()]
            except:
                click.secho( crayons.red("Package not found. Please use ") + crayons.yellow("piper add {}".format(package_line)) + crayons.red("instead"))
                sys.exit(1)

            current_version = overrides.Version.coerce(dep["specs"][0][1])

            coerced_versions = [_item for _item in map(lambda x: overrides.Version.coerce(x, partial=True), original_versions)]
            # version_mapping = map(lambda index, x: (x.__str__(), versions[index] ), enumerate(coerced_versions))

            spec = None
            if upgrade_specifier:
                spec = overrides.Spec(upgrade_specifier)
            elif req.specs:
                spec_line = ",".join(["".join(x) for x in req.specs])
                    # logger.debug("specs {0} {1}".format(spec_line, req.specs))
                spec = overrides.Spec(spec_line)
                # spec = [_item for _item in map(lambda x: overrides.Spec("".join(x) ), req.specs)]
                # logger.error("Investigate")
            else:
                spec = overrides.Spec(">={}".format(current_version.original_version))

            # if dep["specifier"]:
            #     spec = next(map(lambda x: semantic_version.Spec("".join(x) ), dep["specs"]))
            # click.echo("{} {} {}".format(versions, spec, upgrade_specifier))
            if spec:
                valid_versions = [_item for _item in spec.filter(coerced_versions)]
                wanted_version = spec.select(valid_versions).original_version
            else:
                valid_versions = [_item for _item in coerced_versions]
                wanted_version = valid_versions[0]
            patch_version = semantic_version.Spec("~={}".format(current_version.major, current_version.minor, current_version.patch)).select(valid_versions).original_version
            minor_version = semantic_version.Spec("~={}".format(current_version.major, current_version.minor, current_version.patch)).select(valid_versions).original_version

        except ValueError as err:
            logger.debug("ValueError for {0} with {1}".format(dep["name"], err))
            current_version = dep["specs"][0][1]
            # click.echo(err)
            wanted_version = "not semantic"
            patch_version = ""
            minor_version = ""


        # click.echo("{} {} {}".format(versions, spec, upgrade_specifier))
        # valid_versions = list(spec.filter(coerced_versions))
        # wanted_version = spec.select(coerced_versions)

        echo_list = crayons.white("")
        for index, version in enumerate(valid_versions):
            echo_list = echo_list + crayons.yellow("[{}] ".format(index+1)) + crayons.white("{} ".format(version))


        chosen_index = click.prompt("Select one of the following versions: {}".format(echo_list), default=1)
        chosen_version = valid_versions[chosen_index-1]

        package_line = req.name + "==" + chosen_version.__str__()
    else:
        package_line = req.name + upgrade_specifier

    c = pip_install(package_line, allow_global=False, upgrade=True)
    # result = parse.search("Successfully installed {} \n", c.out)

    if not (c.return_code == 0):
        click.secho(c.err, fg="red")
        click.echo(
            crayons.red("Failed to install ") + crayons.yellow(req.name) + crayons.red(" ✗")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )
        sys.exit()
    else:
        click.secho(c.out.rstrip(), fg="blue")

        click.echo(
            crayons.green("Package ") + crayons.yellow(req.name) + crayons.green(" installed ✓")
            # crayons.green("Package {0} installed ✓".format(crayons.yellow(req.name)))
            )


    result = parse.search("Successfully installed {}\n", c.out)
    succesfully_installed = result.fixed[0].split() if result else []
    succesfully_installed = [item.rsplit('-', 1)[0] for item in succesfully_installed]
    existing_packages = [result.fixed[0] for result in parse.findall("Requirement already satisfied: {} in", c.out)]

    all_pkgs = succesfully_installed + existing_packages
    all_pkgs = [Req.parse(pkg).unsafe_name for pkg in all_pkgs]

    # click.secho("Locking requirements...")

    frozen_deps = pip_freeze()
    frozen_dep = next(filter(lambda x: x.name.lower() == req.name.lower(), frozen_deps), None)
    project.update_frozen_dependencies_in_piper_lock(frozen_deps)

    dependency = {
        "name": frozen_dep.name,
        "line": frozen_dep.line,
        "specs": frozen_dep.specs,
        "dependencies": [pkg for pkg in all_pkgs if not (pkg == frozen_dep.name)]
    }
    project.add_dependency_to_piper_lock(dependency, dev=dev)
    project.update_requirement_files_from_piper_lock()

    click.secho("Requirements locked ✓", fg="green")

    # click.echo("All pkgs: {}".format(all_pkgs))

    # click.secho("Updating requirement files...")

    # if (not req.vcs) and (not req.local_file) and req.specs:
    #     add_to_requirements_file(req, os.path.join(".", "requirements", "base.txt"))
    # else:
    #     add_to_requirements_file(frozen_dep, os.path.join(".", "requirements", "base.txt"))
    # add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

    click.secho("Requirements updated ✓", fg="green")
    # compile_requirements(os.path.join(".", "requirements", "base.txt"), os.path.join(".", "requirements", "base-locked.txt"))

    # print(req.__dict__)

    click.echo(
        crayons.green(emoji.emojize("\n:sparkles:  Upgrade complete", use_aliases=True))
    )

@check_before_running
def upgrade_all(upgrade_level="latest", noinput=False):

    pkgs = get_packages_from_requirements_file(project.requirements_file("dev-locked.txt"))
    for package in pkgs:
        upgrade(upgrade_level, noinput=noinput)

@check_before_running
def why(package_name):
    piper_file = project.piper_file
    if package_name.lower() in piper_file["dependencies"]:
        click.echo( crayons.green(package_name) + " exists because it's specified in " + crayons.yellow("dependencies"))
        return
    if package_name.lower() in piper_file["dev_dependencies"]:
        click.echo( crayons.green(package_name) + " exists because it's specified in " + crayons.yellow("dev_dependencies"))
        return
    tree = get_dependency_tree()

    parents = []
    for node in tree:
        found = [dep for dep in node["dependencies"] if (dep["package_name"].lower() == package_name.lower())]
        if found:
            parents.append(node["package"])
    for parent in parents:
        click.echo('The module {0} depends on {1}'.format(crayons.green(parent["package_name"]), crayons.yellow(package_name)))

def dependency_list(depth=None):
    tree = get_dependency_tree()
    # click.echo(json.dumps(tree, indent=4))

    piper_file = project.piper_file
    base_keys = [_key for _key in piper_file["dependencies"]]
    dev_keys = [_key for _key in piper_file["dev_dependencies"]]

    click.echo(
        "# " + crayons.green("base = green") + " | " + crayons.magenta("dev = magenta") + " | " + crayons.cyan("sub dependencies = cyan")
    )

    for node in tree:
        name = node["package"]["package_name"]
        if node["package"]["package_name"].lower() in IGNORED_PACKAGES:
            continue
        elif node["package"]["package_name"].lower() in base_keys:
            name = crayons.green(node["package"]["package_name"])
        elif node["package"]["package_name"].lower() in dev_keys:
            name = crayons.magenta(node["package"]["package_name"])
        else:
            name = crayons.cyan(node["package"]["package_name"])

        click.echo("├─ {0}=={1}".format(name, node["package"]["installed_version"]))
        for dep in node["dependencies"]:
            version_string = dep["required_version"] or ""
            click.echo("│  └─ {0}{1}".format(dep["package_name"], version_string))

    click.echo(
        crayons.green(emoji.emojize("\n:sparkles:  Package list complete", use_aliases=True))
    )


@check_before_running
def wipe():
    click.confirm("Are you sure you want to wipe?", abort=True)
    project.wipe()

@check_before_running
def info(package_name):
    text = pip_show(package_name)
    click.echo(text)

@check_before_running
def version(noinput=False, set_version=None, set_git=False):
    # if new:
    #     # update version

    # else:
    #     # show current version
    click.echo(
        "Your " + crayons.green("project version") + " is " + crayons.yellow(project.piper_file["version"])
    )
    if project.is_git_repository:
        git_tag = project.git_tag
        if git_tag:
            click.echo(
                "You last " + crayons.green("git tag") + " is " + crayons.yellow(project.git_tag)
            )
        else:
            click.echo(
                crayons.yellow("No git tags have been created")
            )
    else:
        click.echo(crayons.yellow("There is no local git repository setup"))
    if not noinput:
        set_version = click.confirm("Do you wish to update the version?")
        if not set_version:
            sys.exit(0)
        version = click.prompt("New version (current version is {})".format(crayons.yellow(project.piper_file["version"])))
        updated_piper_file = project.piper_file.copy()
        updated_piper_file["version"] = version
        project.save_to_piper_file(updated_piper_file)

        if project.is_git_repository:
            set_git = click.confirm("Would you like to create a " + crayons.green("git tag") + " for this version?")
            if set_git:
                project.set_git_tag(version)

        click.secho("Done", fg="green")


@check_before_running
def activate():
    activate_bin = which("activate")
    if os.name == 'nt':
        click.echo(activate_bin.replace(".exe", ".bat"))
    else:
        click.echo("source {}".format(shellquote(activate_bin)))


from .vendor.hashin import get_package_hashes

@check_before_running
def hash():
    click.secho("[1/2] ⌛  Calculating hashes...", fg="yellow")
    lock = project.piper_lock

    frozen = list(lock["frozen_deps"].items())
    with click.progressbar(frozen, length=len(frozen)) as bar:
        for key, val in bar:
            try:
                version = val["specs"][0][1]
                hashes = get_package_hashes(key, version)
                lock["frozen_deps"][key]["hashes"] = hashes["hashes"]
                logger.debug("Saved hashes for: {}".format(val["line"]))
            except Exception as err:
                logger.error("Couldn't get hashes for {0} {1}".format(val["line"], err))
                continue

    click.secho("[2/2] 💾  Storing hashes...", fg="yellow")
    project.save_to_piper_lock(lock)
    project.update_requirement_files_from_piper_lock()

    click.secho("Done", fg="green")

@check_before_running
def cache(output_dir="./piper_cache", dev=False):
    click.secho("[1/2] 🔍  Collecting packages to cache...", fg="yellow")
    # click.secho("Output dir selected: {}".format(output_dir))

    if dev:
        requirements = project.requirements_file("dev-locked.txt").abspath()
    else:
        requirements = project.requirements_file("base-locked.txt").abspath()

    click.secho("[2/2] 📦  Caching packages...", fg="yellow")

    with click_spinner.spinner():
        c = pip_wheel(output_dir, requirements)
        # click.secho(c.out + c.err)
    click.secho("Caching complete! Your cahce is stored at: {}".format(output_dir), fg="green")

def check_integrity():
    pass

@check_before_running
def fix():
    project.denormalise_piper_lock()
    project.prune_frozen_deps()
    project.update_requirement_files_from_piper_lock()

# def run_bin(bin_name, args):
#     path = which(bin_name)
#     if not Path(path).exists():
#         click.secho("Couldn't find {} in the virtualenv".format(bin_name))
#         sys.exit(1)
#     c = delegator.run("{0} {1}".format())

if __name__ == "__main__":
    os.chdir("..")
    # init()
    # add("fabric==1.5")
    # add("fabric")
    # add("django>1.10")
    # add("-e git+https://github.com/requests/requests.git#egg=requests")
    # remove("fabric")
    # remove("django")
    # remove("requests")
    # install()
    outdated()
