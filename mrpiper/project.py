import os
import sys
import errno
from os.path import expanduser
import re
import hashlib
import datetime
# from sets import Set

import simplejson as json
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
        if not self.has_piper_lock:
            self.create_piper_lock()

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

    @property
    def piper_lock_dir(self):
        return os.path.join(".", ".piper")

    @property
    def has_piper_lock(self):
        return os.path.exists(self.piper_lock_dir)

    def create_piper_lock(self):
        tpl = {
            "created": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),

            "dependencies": {

            },

            "devDependencies": {

            }
        }
        json.dump(tpl, open(self.piper_lock_dir, "w"), indent=4 * ' ')

    def add_dependency_to_piper_lock(self, dep, dev=False):
        lock = json.load(open(self.piper_lock_dir, "r"))

        dependency = {
            "depends_on": dep["dependencies"]
        }

        lock["depended_on"] = set(lock["depended_on"] + dependency["depends_on"]) if ("depended_on" in lock) else set(dependency["depends_on"])
        lock["depended_on"] = list(lock["depended_on"])

        if not dev:
            lock["dependencies"][dep["name"]] = dependency
        else:
            lock["devDependencies"][dep["name"]] = dependency

        json.dump(lock, open(self.piper_lock_dir, "w"), indent=4 * ' ')
        return


    def remove_dependency_to_piper_lock(self, dep, dev=False):
        lock = json.load(open(self.piper_lock_dir, "r"))

        if not dev:
            del lock["dependencies"][dep["name"]]
        else:
            del lock["devDependencies"][dep["name"]]

        json.dump(lock, open(self.piper_lock_dir, "w"), indent=4 * ' ')
        return

    def add_frozen_dependencies_to_piper_lock(self, frozen_deps):
        lock = json.load(open(self.piper_lock_dir, "r"))
        lock["frozen_deps"] = {}
        for dep in frozen_deps:
            lock["frozen_deps"][dep.name] = dep.__dict__

        json.dump(lock, open(self.piper_lock_dir, "w"), indent=4 * ' ')
        return

    @property
    def piper_lock(self):
        return json.load(open(self.piper_lock_dir, "r"))