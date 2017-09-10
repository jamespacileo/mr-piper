import os
import sys
import errno
from os.path import expanduser
import re
import hashlib

import delegator

class PythonProject(object):
    
    _virtualenv_location = None
    _requirements_location = None
    _parent_dir = "."

    _home_dir = expanduser("~")

    def __init__(self, path=None):
        pass

    @property
    def virtualenv(self):
        pass

    def pip(self):
        pass


    def has_pipfile(self):
        pass

    def setup(self):
        if not self.has_virtualenv:
            self.create_virtualenv()
        if not self.has_requirements_structure:
            self.create_requirements_structure()

    def has_requirements_structure(self):
        filenames = [
            "base.txt", "base-locked.txt", "dev.txt", "dev-locked.txt"
        ]
        all_exists = True
        for filename in filenames:
            all_exists = all_exists and os.path.exists(os.path.join("./requirements", filename))
        return all_exists

    def create_requirements_structure(self):
        filenames = [
            "base.txt", "base-locked.txt", "dev.txt", "dev-locked.txt"
        ]
        try:
            os.makedirs("./requirements", )
        except OSError as exec:
            if exec.errno == errno.EEXIST and os.path.isdir("./requirements"):
                pass
            else:
                raise
        for filename in filenames:
            with open(os.path.join("./requirements/", filename), "w") as file:
                file.write("")
                file.close()

    @property
    def virtualenv_dir(self):
        # global_virtualenv_dir = os.path.join(self._home_dir, ".envs")
        # complete_dir = os.path.join(global_virtualenv_dir)
        return os.path.join(self._parent_dir, ".virtualenvs", "project_virtualenv")

    @property
    def has_virtualenv(self):
        return os.path.isdir(self.virtualenv_dir)

    def create_virtualenv(self):

        c = delegator.run("virtualenv {0}".format(self.virtualenv_dir))
        c.block()
        return c.return_code == 0
