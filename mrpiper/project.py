# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import str as text
from builtins import map, filter

import collections
import os
import sys
import errno
from os.path import expanduser
import re
import hashlib
import datetime
import shutil
import itertools
import logging
logger = logging.getLogger("mrpiper.cli")

import click
import click_spinner
import crayons
# from sets import Set

from path import Path
import simplejson as json
import delegator

from . import utils


CORE_PACKAGES = ["pip", "setuptools", "piper"]

REQUIREMENT_FILE_GENERATED_TEXT = """# This file was autogenerated by PIPER, please don't edit this file directly."""

setup_py_template = (Path(os.path.dirname(__file__)) / "templates" / "setup.py.tpl")

class PythonProject(object):

    # _virtualenv_location = None
    # _requirements_location = None
    # _parent_dir = "."

    # _home_dir = expanduser("~")

    def __init__(self, path=None):
        self.detect_virtualenv_location()

    @property
    def virtualenv(self):
        pass

    def pip(self):
        pass

    def has_pipfile(self):
        pass

    def setup(self, noinput=False, init_data={}, python=None, virtualenv_location="inside", installable=False):
        click.secho("Creating virtualenv...", fg="yellow")
        if not self.has_virtualenv:
            # self.virtualenv_location = virtualenv_location
            with click_spinner.spinner():
                self.create_virtualenv(python=python, virtualenv_location=virtualenv_location)
            click.secho("Virtualenv created ✓", fg="green")
            click.secho("Your virtualenv path: " + crayons.magenta("{}".format(self.virtualenv_dir)))
        else:
            click.secho("Virtualenv already exists ✓", fg="green")

        click.secho("Creating requirement files...", fg="yellow")
        if not self.has_requirements_structure:
            self.create_requirements_structure()
            click.secho("Requirement files created ✓", fg="green")
        else:
            click.secho("Requirement files already exists ✓", fg="green")

        click.secho("Creating piper file...", fg="yellow")
        if not self.has_piper_file:
            self.create_piper_file(noinput=noinput, init_data=init_data)
            click.secho("Piper file created ✓", fg="green")
        else:
            click.secho("Piper file already exists ✓", fg="green")

        click.secho("Creating piper lock...", fg="yellow")
        if not self.has_piper_lock:
            self.create_piper_lock()
            click.secho("Piper lock created ✓", fg="green")
        else:
            click.secho("Piper lock already exists ✓", fg="green")

        if not self.has_setup_py:
            if (not installable) and (not noinput):
                wants_setup_py = click.confirm("Do you want to make the project installable (adding setup.py)?")
                installable = wants_setup_py

            if installable:
                self.setup_py_dir.write_text(setup_py_template.text())
                click.secho("setup.py created ✓", fg="green")
            else:
                click.secho("setup.py creation skipped", fg="yellow")

        logger.debug([
            self.virtualenv_dir,
            self.piper_file_dir,
            self.piper_lock_dir,
            self.requirements_dir
        ])

    def validate(self):
        lock = self.piper_lock

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

    def wipe(self):
        try:
            shutil.rmtree(self.virtualenv_dir)
        except OSError as err:
            pass
        try:
            shutil.rmtree(self.requirements_dir)
        except OSError as err:
            pass
        try:
            os.remove(self.piper_lock_dir)
        except OSError as err:
            pass
        try:
            os.remove(self.piper_file_dir)
        except OSError as err:
            pass

    @property
    def setup_py_dir(self):
        return self.project_dir / "setup.py"

    @property
    def has_setup_py(self):
        return self.setup_py_dir.exists()

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

    _virtualenv_location = None
    @property
    def virtualenv_location(self):
        return self._virtualenv_location

    @property
    def virtualenv_inside_dir(self):
        return self.project_dir / ".virtualenvs" / "project_virtualenv"


    _virtualenv_outside_dir = None
    @property
    def virtualenv_outside_dir(self):
        if not self._virtualenv_outside_dir:
            hashed_name = "{0}_{1}".format(
                self.project_dir.name,
                hashlib.sha256(str(self.project_dir.abspath()).encode("utf-8")).hexdigest()[:6]
            )
            self._virtualenv_outside_dir = Path("~").expanduser() / ".local" / "share" / "piper_virtualenv" / hashed_name
        return self._virtualenv_outside_dir

    @property
    def virtualenv_dir(self):
        # global_virtualenv_dir = os.path.join(self._home_dir, ".envs")
        # complete_dir = os.path.join(global_virtualenv_dir)
        # return self.project_dir / ".virtualenvs" / "project_virtualenv"
        if self.virtualenv_location == "inside":
            return self.virtualenv_inside_dir
        if self.virtualenv_location == "outside":
            return self.virtualenv_outside_dir
        # raise Exception("Shouldn't happen")
        return self.virtualenv_inside_dir

    def detect_virtualenv_location(self):
        if self.virtualenv_inside_dir.exists(): #inside
            self._virtualenv_location = "inside"
            return True
        if self.virtualenv_outside_dir.exists(): #outside
            self._virtualenv_location = "outside"
            return True
        return False

    @property
    def has_virtualenv(self):
        if self.virtualenv_inside_dir.exists(): #inside
            self._virtualenv_location = "inside"
            return True
        if self.virtualenv_outside_dir.exists(): #outside
            self._virtualenv_location = "outside"
            return True
        return False

    def create_virtualenv(self, python=None, virtualenv_location="inside"):
        virtualenv_dir = self.virtualenv_inside_dir if (virtualenv_location == "inside") else self.virtualenv_outside_dir
        if python:
            command = "virtualenv {0} --python={1}".format(
                utils.shellquote(virtualenv_dir.abspath()),
                utils.shellquote(python)
                )
        else:
            command = "virtualenv {0}".format(
                utils.shellquote(virtualenv_dir.abspath()),
            )
        self._virtualenv_location = virtualenv_location
        # click.echo(command)
        c = delegator.run(command)
        return c.return_code == 0

    @property
    def piper_file_dir(self):
        return self.project_dir / "piper.json"

    @property
    def piper_file(self):
        return json.loads(self.piper_file_dir.text(), object_pairs_hook=collections.OrderedDict)

    @property
    def has_piper_file(self):
        return self.piper_file_dir.exists()

    @property
    def piper_lock_dir(self):
        return self.project_dir / "piper.lock"

    @property
    def has_piper_lock(self):
        return self.piper_lock_dir.exists()

    def save_to_piper_lock(self, data):
        self.piper_lock_dir.write_text(text(json.dumps(data, indent=4 * ' ')))

    def save_to_piper_file(self, data):
        self.piper_file_dir.write_text(text(json.dumps(data, indent=4 * ' ')))

    def create_piper_file(self, noinput=False, init_data={}):
        package_name = init_data.get("package_name", self.project_dir.name)
        author = init_data.get("author", "")
        src = init_data.get("src", "src")
        version = init_data.get("version", "0.0.1")
        description = init_data.get("description", "")
        repository = init_data.get("repository", "")
        licence = init_data.get("licence", "")
        private = init_data.get("private", False)
        if not noinput:
            package_name = click.prompt("Project name", default=package_name)
            author = click.prompt("Author", default=author)
            src = click.prompt("Source directory", default=src)
            version = click.prompt("Version", default=version)
            description = click.prompt("Description", default=description)
            repository = click.prompt("Repository", default=repository)
            licence = click.prompt("Licence", default=licence)
            private = click.prompt("Is it a private project?", default=private, type=bool)

        tpl = collections.OrderedDict([
            ("created", datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
            ("name", package_name),
            ("version", version),
            ("description", description),
            ("source_dir", src),
            ("repository", description),
            ("author", author),
            ("license", licence),
            ("dependencies", {}),
            ("devDependencies", {}),
        ])
        self.save_to_piper_file(tpl)

    def create_piper_lock(self):
        tpl = collections.OrderedDict([
            ("created", datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
            ("dependencies", {}),
            ("devDependencies", {}),
            ("dependables", []),
            ("frozen_deps", {}),
        ])
        self.save_to_piper_lock(tpl)

    def add_dependency_to_piper_lock(self, dep, dev=False):
        lock = self.piper_lock
        piper_file = self.piper_file

        dependency = {
            "depends_on": list(filter(lambda x: not (x in CORE_PACKAGES), dep["dependencies"])),
            "line": dep["line"]
        }

        # lock["depended_on"] = set(lock["depended_on"] + dependency["depends_on"]) if ("depended_on" in lock) else set(dependency["depends_on"])
        # lock["depended_on"] = list(lock["depended_on"])

        if not dev:
            piper_file["dependencies"][dep["name"].lower()] = dep["line"]
            lock["dependencies"][dep["name"].lower()] = dependency

            if dep["name"].lower() in lock["devDependencies"]: #.keys():
                del lock["devDependencies"][dep["name"].lower()]
            if dep["name"].lower() in piper_file["devDependencies"]: #.keys():
                del piper_file["devDependencies"][dep["name"].lower()]
        else:
            piper_file["devDependencies"][dep["name"].lower()] = dep["line"]
            lock["devDependencies"][dep["name"].lower()] = dependency

            if dep["name"].lower() in lock["dependencies"]: #.keys():
                del lock["dependencies"][dep["name"].lower()]
            if dep["name"].lower() in piper_file["dependencies"]: #.keys():
                del piper_file["dependencies"][dep["name"].lower()]

        self.save_to_piper_lock(lock)
        self.save_to_piper_file(piper_file)
        # json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')

        self.denormalise_piper_lock()
        return


    def remove_dependency_to_piper_lock(self, dep_name):
        lock = self.piper_lock
        piper_file = self.piper_file

        if dep_name.lower() in lock["dependencies"]: #.keys():
            del lock["dependencies"][dep_name.lower()]
        if dep_name.lower() in piper_file["dependencies"]: #.keys():
            del piper_file["dependencies"][dep_name.lower()]

        if dep_name.lower() in lock["devDependencies"]: #.keys():
            del lock["devDependencies"][dep_name.lower()]
        if dep_name.lower() in piper_file["devDependencies"]: #.keys():
            del piper_file["devDependencies"][dep_name.lower()]


        self.save_to_piper_lock(lock)
        self.save_to_piper_file(piper_file)
        # json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')

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
            if key.lower() in dependencies: #.keys():
                base_main.append(item)
                base_locked.append(item)
                continue
            list_of_dependables = map(lambda x: x[1]["depends_on"], dependencies.items())
            if key.lower() in itertools.chain.from_iterable(list_of_dependables):
                base_locked.append(item)
                continue

            if key.lower() in devDependencies: #.keys():
                dev_main.append(item)
                dev_locked.append(item)
                continue
            list_of_dev_dependables = map(lambda x: x[1]["depends_on"], devDependencies.items())
            if key.lower() in itertools.chain.from_iterable(list_of_dev_dependables):
                dev_locked.append(item)
                continue

        logger.debug([base_main, base_locked, dev_main, dev_locked])

        self.requirements_file("base.txt").write_lines(
            [REQUIREMENT_FILE_GENERATED_TEXT, ""] + [item["line"] for item in base_main]
        )
        self.requirements_file("base-locked.txt").write_lines(
            [REQUIREMENT_FILE_GENERATED_TEXT, ""] + [item["line"] for item in base_locked]
        )
        self.requirements_file("dev.txt").write_lines(
            [REQUIREMENT_FILE_GENERATED_TEXT, "-r base.txt", ""] + [item["line"] for item in dev_main]
        )
        self.requirements_file("dev-locked.txt").write_lines(
            [REQUIREMENT_FILE_GENERATED_TEXT, "-r base-locked.txt", ""] + [item["line"] for item in dev_locked]
        )

    def denormalise_piper_lock(self):
        lock = self.piper_lock

        dependencies = lock["dependencies"].items()
        devDependencies = lock["devDependencies"].items()
        allDeps = itertools.chain(dependencies, devDependencies)

        allDependendables = map(lambda x: x[1]["depends_on"], allDeps)
        allChainedDependables = itertools.chain.from_iterable(allDependendables)
        lock["dependables"] = list(set(allChainedDependables))

        # lock["depended_on"] = set(lock["depended_on"] + dependency["depends_on"]) if ("depended_on" in lock) else set(dependency["depends_on"])
        # lock["depended_on"] = list(lock["depended_on"])

        self.save_to_piper_lock(lock)
        # json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')
        return

    def update_piper_lock_from_piper_file_and_tree(self, tree):
        piper_file = self.piper_file
        lock = self.piper_lock

        deps = [key for key in piper_file.get("dependencies", {})]
        devDeps = [key for key in piper_file.get("devDependencies", {})]

        base_dependencies = {}
        for dep in deps:
            for package in tree:
                if package["package"]["package_name"] == dep:
                    item = {
                        "line": "{0}=={1}".format(
                            package["package"]["package_name"],
                            package["package"]["installed_version"]
                        ),
                        "depends_on": [item["package_name"] for item in package["dependencies"]]
                    }
                    base_dependencies[dep.lower()] = item

        dev_dependencies = {}
        for dep in devDeps:
            for package in tree:
                if package["package"]["package_name"] == dep:
                    item = {
                        "line": "{0}=={1}".format(
                            package["package"]["package_name"],
                            package["package"]["installed_version"]
                        ),
                        "depends_on": [item["package_name"] for item in package["dependencies"]]
                    }
                    dev_dependencies[dep.lower()] = item


        lock["dependencies"] = base_dependencies
        lock["devDependencies"] = dev_dependencies
        self.save_to_piper_lock(lock)
        self.denormalise_piper_lock()


    def update_frozen_dependencies_in_piper_lock(self, frozen_deps):
        lock = self.piper_lock
        lock["frozen_deps"] = {}
        for dep in frozen_deps:
            if not (dep.name.lower() in CORE_PACKAGES):
                lock["frozen_deps"][dep.name.lower()] = dep.__dict__

        self.save_to_piper_lock(lock)
        # json.dump(lock, self.piper_lock_dir.open("w"), indent=4 * ' ')
        return

    @property
    def piper_lock(self):
        # if not self.piper_lock_dir.exists():
        #     self.create_piper_lock()
        return json.load(self.piper_lock_dir.open("r"), object_pairs_hook=collections.OrderedDict)

    def detect_type_of_dependency(self, package_name):
        lock = self.piper_lock
        if package_name in lock["dependencies"]: #.keys():
            return "base"
        base_dependables = map(lambda x: x[1]["depends_on"], lock["dependencies"].items())
        if package_name in itertools.chain.from_iterable(base_dependables):
            return "base"
        if package_name in lock["devDependencies"]: #.keys():
            return "dev"
        dev_dependables = map(lambda x: x[1]["depends_on"], lock["devDependencies"].items())
        if package_name in itertools.chain.from_iterable(dev_dependables):
            return "dev"
        return None

    def find_removable_dependencies(self, package_name):
        lock = self.piper_lock

        regular = package_name.lower() in lock["dependencies"]#.keys()
        dev = package_name.lower() in lock["devDependencies"]#.keys()

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
