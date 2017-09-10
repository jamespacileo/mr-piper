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
# import pipfile

from .project import PythonProject

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

    pass

def add(package_line, dev=False):
    pass

def remove(package_line):
    pass

def install():
    pass
