import contextlib
import codecs
import json
import os
import sys
import distutils.spawn
import shutil
import signal
import tempfile

import delegator
from vendor.requirements.requirement import Requirement
from vendor.requirements.parser import parse as parse_requirements

# import pipfile

from project import PythonProject

project = PythonProject()

def which(command):
    if os.name == 'nt':
        if command.endswith('.py'):
            return os.sep.join([project.virtualenv_location] + ['Scripts\{0}'.format(command)])
        return os.sep.join([project.virtualenv_location] + ['Scripts\{0}.exe'.format(command)])
    return os.sep.join([project.virtualenv_location] + ['bin/{0}'.format(command)])


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
    req = Requirement.parse(package_line)

    has_specs = len(req.specs) > 0
    is_vcs = req.vcs
    is_local_file = req.local_file
    is_editable = req.editable

    if is_vcs and (not is_editable):
        # print("Make sure ")
        req.editable = True

    if is_vcs and (not req.name):
        print ("Make sure to add #egg=<name>")
        return


    print(req.__dict__)

def remove(package_line):
    pass

def install():
    pass

if __name__ == "__main__":
    init()
    add("fabric==1.5")