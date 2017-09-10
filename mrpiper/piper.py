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

import click
import delegator
from pip.req.req_file import parse_requirements, process_line

from vendor.requirements.requirement import Requirement
from vendor.requirements.parser import parse as parse_requirements

# import pipfile

from utils import add_to_requirements_file, compile_requirements
from project import PythonProject

project = PythonProject()


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
        return False

    # Return the result of the first one that runs ok, or the last one that didn't work.
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

    pip_install(package_line, allow_global=False)
    add_to_requirements_file(req, os.path.join(".", "requirements", "base.txt"))
    compile_requirements(os.path.join(".", "requirements", "base.txt"), os.path.join(".", "requirements", "base-locked.txt"))
    

    print(req.__dict__)

def remove(package_line):
    pass

def install():
    pass


if __name__ == "__main__":
    init()
    add("fabric==1.5")
    add("fabric")
    add("django>1.10")