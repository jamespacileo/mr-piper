import os
import sys
import errno
from os.path import expanduser
import re
import hashlib
import datetime
import shutil
import click
import crayons
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
        click.secho("Creating virtualenv...")
        if not self.has_virtualenv:
            self.create_virtualenv()
            click.secho("Virtualenv created ✓", fg="green")
        else:
            click.secho("Virtualenv already exists ✓", fg="green")

        click.secho("Creating requirement files...")
        if not self.has_requirements_structure:
            self.create_requirements_structure()
            click.secho("Requirement files created ✓", fg="green")
        else:
            click.secho("Requirement files already exists ✓", fg="green")

        click.secho("Creating piper file...")
        if not self.has_piper_lock:
            self.create_piper_lock()
            click.secho("Piper file created ✓", fg="green")
        else:
            click.secho("Piper file already exists ✓", fg="green")

    def clear(self):
        try:
            shutil.rmtree(self.virtualenv_dir)
        except FileNotFoundError as err:
            pass
        try:
            shutil.rmtree(self.requirements_dir)
        except FileNotFoundError as err:
            pass
        try:
            os.remove(self.piper_lock_dir)
        except FileNotFoundError as err:
            pass

    @property
    def requirements_dir(self):
        return os.path.join(".", "requirements")

    @property
    def has_requirements_structure(self):
        filenames = [
            "base.txt", "base-locked.txt", "dev.txt", "dev-locked.txt"
        ]
        all_exists = True
        for filename in filenames:
            all_exists = all_exists and os.path.exists(os.path.join(".", "requirements", filename))
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
            lock["dependencies"][dep["name"].lower()] = dependency
        else:
            lock["devDependencies"][dep["name"].lower()] = dependency

        json.dump(lock, open(self.piper_lock_dir, "w"), indent=4 * ' ')
        return


    def remove_dependency_to_piper_lock(self, dep_name, dev=False):
        lock = json.load(open(self.piper_lock_dir, "r"))

        if not dev:
            del lock["dependencies"][dep_name.lower()]
        else:
            del lock["devDependencies"][dep_name.lower()]

        json.dump(lock, open(self.piper_lock_dir, "w"), indent=4 * ' ')
        return

    def update_frozen_dependencies_in_piper_lock(self, frozen_deps):
        lock = json.load(open(self.piper_lock_dir, "r"))
        lock["frozen_deps"] = {}
        for dep in frozen_deps:
            lock["frozen_deps"][dep.name.lower()] = dep.__dict__

        json.dump(lock, open(self.piper_lock_dir, "w"), indent=4 * ' ')
        return

    @property
    def piper_lock(self):
        return json.load(open(self.piper_lock_dir, "r"))


    def find_removable_dependencies(self, package_name):
        lock = self.piper_lock
        
        regular = package_name.lower() in lock["dependencies"].keys()
        dev = package_name.lower() in lock["devDependencies"].keys()

        if (not regular) and (not dev):
            # click.echo("No")
            return False

        deps = dict(lock["dependencies"])
        deps.update(lock["devDependencies"])

        to_remove = deps[package_name.lower()]["depends_on"]
        locked_dependencies = set()
        for key, value in deps.items():
            if key == package_name.lower():
                continue

            for item in value["depends_on"]:
                locked_dependencies.add(item)

        removable = [item for item in to_remove if not (item in locked_dependencies)]
        return removable
            