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

import parse
import click
import delegator

from pkg_resources import Requirement as Req
from pip.req.req_file import parse_requirements, process_line

from vendor.requirements.requirement import Requirement
from vendor.requirements.parser import parse as parse_requirements

# import pipfile

from utils import add_to_requirements_file, compile_requirements, add_to_requirements_lockfile
from project import PythonProject

project = PythonProject()

def pip_freeze():
    click.echo("Freezing requirements...")
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

def pip_install(
    package_name=None, r=None, allow_global=False, no_deps=False
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

    no_deps = '--no-deps' if no_deps else ''

    pip_command = '"{0}" install {2} {1} --exists-action w'.format(
        which_pip(allow_global=allow_global),
        install_reqs,
        no_deps
    )

    c = delegator.run(pip_command)

    if c.return_code == 0:
        return c

    # Return the result of the first one that runs ok, or the last one that didn't work.
    return c

def pip_uninstall(packages):
    pip_command = "{0} uninstall --yes {1}".format(which_pip(), " ".join(packages))
    click.echo(pip_command)
    c = delegator.run(pip_command)
    return c

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


def init():
    # create requirements structure
    # create virtualenv
    project.setup()

def add(package_line, dev=False):
    # create requirements
    # init()

    req = Requirement.parse(package_line)

    click.echo(req.__dict__)

    has_specs = len(req.specs) > 0
    is_vcs = req.vcs
    is_local_file = req.local_file
    is_editable = req.editable

    if is_vcs and (not is_editable):
        # print("Make sure ")
        req.editable = True
        package_line = "-e {0}".format(package_line)

    if is_vcs and (not req.name):
        print ("Make sure to add #egg=<name>")
        return

    c = pip_install(package_line, allow_global=False)
    # result = parse.search("Successfully installed {} \n", c.out)
    click.echo(c.out)

    result = parse.search("Successfully installed {}\n", c.out)
    succesfully_installed = result.fixed[0].split() if result else []
    existing_packages = [result.fixed[0] for result in parse.findall("Requirement already satisfied: {} in", c.out)]

    all_pkgs = succesfully_installed + existing_packages
    all_pkgs = [Req.parse(pkg).unsafe_name for pkg in all_pkgs]
    
    frozen_deps = pip_freeze()
    frozen_dep = next(filter(lambda x: x.name.lower() == req.name.lower(), frozen_deps), None)
    project.add_frozen_dependencies_to_piper_lock(frozen_deps)

    dependency = {
        "name": frozen_dep.name,
        "specs": frozen_dep.specs,
        "dependencies": [pkg for pkg in all_pkgs if not (pkg == frozen_dep.name)]
    }
    project.add_dependency_to_piper_lock(dependency)

    click.echo("All pkgs: {}".format(all_pkgs))

    if (not req.vcs) and (not req.local_file) and req.specs:
        add_to_requirements_file(req, os.path.join(".", "requirements", "base.txt"))
    else:
        add_to_requirements_file(frozen_dep, os.path.join(".", "requirements", "base.txt"))
    add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))
    # compile_requirements(os.path.join(".", "requirements", "base.txt"), os.path.join(".", "requirements", "base-locked.txt"))
    
    print(req.__dict__)



def find_removable_dependencies(package_name):
    pass

def remove(package_line):
    req = Requirement.parse(package_line)
    click.echo(req.__dict__)
    
    removable_packages = project.find_removable_dependencies(req.name)
    if removable_packages:
        c = pip_uninstall(removable_packages)
    else:
        c = pip_uninstall(req.name)
    click.echo(c.out)

    frozen_deps = pip_freeze()
    project.add_frozen_dependencies_to_piper_lock(frozen_deps)
    add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

def install():
    pass


if __name__ == "__main__":
    os.chdir("..")
    init()
    # add("fabric==1.5")
    add("fabric")
    # add("django>1.10")
    # add("-e git+https://github.com/requests/requests.git#egg=requests")
    remove("fabric")
    remove("django")
    remove("requests")