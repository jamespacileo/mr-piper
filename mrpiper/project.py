import os
import sys
import errno
from os.path import expanduser
import re
import hashlib
import datetime
import shutil
import itertools

import click
import crayons
# from sets import Set

from path import Path
import simplejson as json
import delegator

CORE_PACKAGES = ["pip", "setuptools", "piper"]

class PythonProject(object):
    
    # _virtualenv_location = None
    # _requirements_location = None
    # _parent_dir = "."

    # _home_dir = expanduser("~")

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

    def is_inside_project(self, path):
        
        parent, name = path.splitpath()
        piper_files = [item for item in path.files("piper.json")]
        if piper_files:
            return path
        
        # print(parent)
        if name:
            self.is_inside_project(parent)
        return False

    _project_dir = None

    @property
    def project_dir(self):
        if not self._project_dir:
            result = self.is_inside_project(Path(os.getcwd()))
            if result:
                self._project_dir = result
            else:
                self._project_dir = Path(os.getcwd())
        return self._project_dir

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
        return self.project_dir / "requirements"

    def requirements_file(self, name):
        return self.requirements_dir / name

    @property
    def has_requirements_structure(self):
        filenames = [
            "base.txt", "base-locked.txt", "dev.txt", "dev-locked.txt"
        ]
        all_exists = True
        for filename in filenames:
            all_exists = all_exists and (self.requirements_dir / filename).exists()
        return all_exists

    def create_requirements_structure(self):
        filenames = [
            "base.txt", "base-locked.txt", "dev.txt", "dev-locked.txt"
        ]
        self.requirements_dir.mkdir_p()
        # try:
        #     os.makedirs("./requirements", )
        # except OSError as exec:
        #     if exec.errno == errno.EEXIST and os.path.isdir("./requirements"):
        #         pass
        #     else:
        #         raise
        for filename in filenames:
            (self.requirements_dir / filename).touch()
            # with open(os.path.join("./requirements/", filename), "w") as file:
            #     file.write("")
            #     file.close()

    @property
    def virtualenv_dir(self):
        # global_virtualenv_dir = os.path.join(self._home_dir, ".envs")
        # complete_dir = os.path.join(global_virtualenv_dir)
        return self.project_dir / ".virtualenvs" / "project_virtualenv"

    @property
    def has_virtualenv(self):
        return self.virtualenv_dir.isdir()

    def create_virtualenv(self):
        command = "virtualenv {0}".format(self.virtualenv_dir)
        # click.echo(command)
        c = delegator.run(command)
        return c.return_code == 0

    @property
    def piper_lock_dir(self):
        return self.project_dir / "piper.json"

    @property
    def has_piper_lock(self):
        return self.piper_lock_dir.exists()

    def create_piper_lock(self):
        tpl = {
            "created": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),

            "dependencies": {

            },

            "devDependencies": {

            }
        }
        json.dump(tpl, self.piper_lock_dir.open("w"), indent=4 * ' ')

    def add_dependency_to_piper_lock(self, dep, dev=False):
        lock = json.load(self.piper_lock_dir.open("r"))

        dependency = {
            "depends_on": list(filter(lambda x: not (x in CORE_PACKAGES), dep["dependencies"])),
            "line": dep["line"]
        }

        # lock["depended_on"] = set(lock["depended_on"] + dependency["depends_on"]) if ("depended_on" in lock) else set(dependency["depends_on"])
        # lock["depended_on"] = list(lock["depended_on"])

        if not dev:
            lock["dependencies"][dep["name"].lower()] = dependency
            if dep["name"].lower() in lock["devDependencies"].keys():
                del lock["devDependencies"][dep["name"].lower()]
        else:
            lock["devDependencies"][dep["name"].lower()] = dependency
            if dep["name"].lower() in lock["dependencies"].keys():
                del lock["dependencies"][dep["name"].lower()]

        json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')

        self.denormalise_piper_lock()
        return


    def remove_dependency_to_piper_lock(self, dep_name):
        lock = json.load(self.piper_lock_dir.open("r"))

        if dep_name.lower() in lock["dependencies"].keys():
            del lock["dependencies"][dep_name.lower()]

        if dep_name.lower() in lock["devDependencies"].keys():
            del lock["devDependencies"][dep_name.lower()]

        json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')

        self.denormalise_piper_lock()
        return

    def update_requirement_files_from_piper_lock(self):
        lock = json.load(self.piper_lock_dir.open("r"))

        frozen = lock["frozen_deps"]

        dependencies = lock["dependencies"]
        devDependencies = lock["devDependencies"]

        base_main = []
        base_locked = []
        dev_main = []
        dev_locked = []

        # iterate frozen and detect if needs to be in base.txt or dev.txt
        for key, item in frozen.items():
            if key.lower() in dependencies.keys():
                base_main.append(item)
                base_locked.append(item)
                continue
            list_of_dependables = map(lambda x: x[1]["depends_on"], dependencies.items())
            if key.lower() in itertools.chain.from_iterable(list_of_dependables):
                base_locked.append(item)
                continue
            
            if key.lower() in devDependencies.keys():
                dev_main.append(item)
                dev_locked.append(item)
                continue
            list_of_dev_dependables = map(lambda x: x[1]["depends_on"], devDependencies.items())
            if key.lower() in itertools.chain.from_iterable(list_of_dev_dependables):
                dev_locked.append(item)
                continue

        click.echo([base_main, base_locked, dev_main, dev_locked])

        self.requirements_file("base.txt").write_lines(
            [item["line"] for item in base_main]
        )
        self.requirements_file("base-locked.txt").write_lines(
            [item["line"] for item in base_locked]
        )
        self.requirements_file("dev.txt").write_lines(
            ["-r base.txt", ""] + [item["line"] for item in dev_main]
        )
        self.requirements_file("dev-locked.txt").write_lines(
            ["-r base-locked.txt", ""] + [item["line"] for item in dev_locked]
        )
        
    def denormalise_piper_lock(self):
        lock = json.load(self.piper_lock_dir.open("r"))

        dependencies = lock["dependencies"].items()
        devDependencies = lock["devDependencies"].items()
        allDeps = itertools.chain(dependencies, devDependencies)

        allDependendables = map(lambda x: x[1]["depends_on"], allDeps)
        allChainedDependables = itertools.chain.from_iterable(allDependendables)
        lock["dependables"] = list(set(allChainedDependables))

        # lock["depended_on"] = set(lock["depended_on"] + dependency["depends_on"]) if ("depended_on" in lock) else set(dependency["depends_on"])
        # lock["depended_on"] = list(lock["depended_on"])

        json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')
        return

    def update_frozen_dependencies_in_piper_lock(self, frozen_deps):
        lock = json.load(self.piper_lock_dir.open("r"))
        lock["frozen_deps"] = {}
        for dep in frozen_deps:
            if not (dep.name.lower() in CORE_PACKAGES):
                lock["frozen_deps"][dep.name.lower()] = dep.__dict__

        json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')
        return

    @property
    def piper_lock(self):
        return json.load(self.piper_lock_dir.open("r"))

    def detect_type_of_dependency(self, package_name):
        lock = self.piper_lock
        if package_name in lock["dependencies"].keys():
            return "base"
        base_dependables = map(lambda x: x[1]["depends_on"], lock["dependencies"].items())
        if package_name in itertools.chain.from_iterable(base_dependables):
            return "base"
        if package_name in lock["devDependencies"].keys():
            return "dev"
        dev_dependables = map(lambda x: x[1]["depends_on"], lock["devDependencies"].items())
        if package_name in itertools.chain.from_iterable(dev_dependables):
            return "dev"
        return None

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
            