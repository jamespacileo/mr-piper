# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import platform

import tempfile
import delegator

from path import Path

# sys.path.append(os.path.join(os.path.abspath(__file__), ".."))
# print(os.path.join(os.path.realpath(__file__), ".."))
sys.path.append(".")
sys.path.append("..")
from mrpiper import piper

source_path = Path("..") / "mrpiper"

TESTS_LOCATION = os.getcwd()
TEMP_LOCATION = tempfile.mkdtemp()
# TEMP_LOCATION = "C:\\Users\\james\\AppData\\Local\\Temp\\tmp6q_l1n1g"
project_dir = Path(TEMP_LOCATION)
project_dir.chdir()
req_folder = (project_dir / "requirements")

base_txt = (req_folder / "base.txt")
base_locked_txt = (req_folder / "base-locked.txt")
dev_txt = (req_folder / "dev.txt")
dev_locked_txt = (req_folder / "dev-locked.txt")
piper_file = (project_dir / "piper.json")
virtualenv_dir = (project_dir / ".virtualenvs" / "project_virtualenv")

try:
    command = 'code-insiders.cmd "{}"'.format(project_dir)
    # print(command)
    if (platform.system() == "Windows"):
        delegator.run(command, block=False)
except:
    pass

def create_test_project():
    temp_project_dir = tempfile.mkdtemp()

def test_installing_itself():
    with source_path:
        c = delegator.run("piper add .")
        print(c.out + c.err)
        assert c.return_code == 0

def test_init():
    piper.init(noinput=True, private=True)
    assert req_folder.exists()
    assert base_txt.exists()
    assert base_locked_txt.exists()
    assert dev_txt.exists()
    assert dev_locked_txt.exists()
    assert piper_file.exists()
    assert virtualenv_dir.exists()

def test_add():
    piper.add("requests")
    assert base_txt.isfile()
    assert "requests" in base_txt.text()

    piper.add("Werkzeug")
    assert "Werkzeug" in base_txt.text()

    piper.add("regex")
    assert "regex" in base_txt.text()

    piper.remove("requests")
    piper.add("git+https://github.com/requests/requests.git@v2.18.4#egg=requests")
    assert "requests" in base_txt.text()

    if not (platform.system() == "Windows"):
        piper.add("git+https://github.com/scrapy/scrapy.git#egg=scrapy")
        assert "scrapy" in base_txt.text()

    piper.add("path.py", dev=True)
    assert dev_txt.isfile()
    assert "path.py" in dev_txt.text()



def test_remove():
    piper.remove("requests")
    assert base_txt.isfile()
    assert not ("requests" in base_txt.text())

    if not (platform.system() == "Windows"):
        piper.remove("scrapy")
        assert base_txt.isfile()
        assert not ("scrapy" in base_txt.text())

    piper.remove("path.py")
    assert dev_txt.isfile()
    assert not ("requests" in dev_txt.text())

    lock = piper.project.piper_lock
    assert not lock["dependencies"].keys()
    assert not lock["devDependencies"].keys()
    assert not lock["dependables"]
    assert not lock["frozen_deps"].keys()


def test_upgrade():
    piper.add("requests==2.0.0", dev=True)
    piper.upgrade("requests", upgrade_level="patch", noinput=True)
    assert ("requests==2.0.1" in dev_txt.text())

    piper.add("requests==1.0.0", dev=True)
    piper.upgrade("requests", upgrade_level="patch", noinput=True)
    assert ("requests==1.0.4" in dev_txt.text())
    piper.upgrade("requests", upgrade_level="minor", noinput=True)
    assert ("requests==1.2.3" in dev_txt.text())
    piper.upgrade("requests", upgrade_level="major", noinput=True)
    assert ("requests==2." in dev_txt.text())
    # piper.upgrade("requests<2.0.0", major=True, noinput=True)
    # assert ("requests==1.2.3" in dev_txt.text())

    # Check warning for editables

    # Version selection



def test_outdated():
    piper.outdated(all_pkgs=True)
    piper.add("requests==2.16.0", dev=True)
    # piper.add("pytest", dev=True)
    # piper.upgrade("requests", patch=True)
    assert ("requests" in dev_txt.text())
    piper.outdated(all_pkgs=True, verbose=True)


def test_install():
    piper.add("requests")
    piper.add("pytest", dev=True)
    piper.add("six")
    piper.add("coverage", dev=True)
    piper.project.virtualenv_dir.rmtree_p()
    piper.project.piper_lock_dir.remove_p()
    piper.install()
    frozen_deps = [item.name for item in piper.pip_freeze()]
    assert "requests" in frozen_deps
    assert "pytest" in frozen_deps
    assert "six" in frozen_deps
    assert "coverage" in frozen_deps
    # assert ("requests" in dev_txt.text())

if __name__=="__main__":
    test_init()
    test_add()
    test_remove()
    test_upgrade()
    test_outdated()
    test_install()
