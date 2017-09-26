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


# source_path = Path("..") / "mrpiper"
source_path = Path(Path("mrpiper").abspath())

LOCAL_TEST_PROJECT = False

if LOCAL_TEST_PROJECT:
    TEMP_LOCATION = Path("temp") / "temp_project"
    Path("temp").mkdir_p()
    TEMP_LOCATION.rmtree_p()
    TEMP_LOCATION.mkdir_p()
    project_dir = Path(TEMP_LOCATION.abspath())
else:
    TEMP_LOCATION = tempfile.mkdtemp()
    project_dir = Path(TEMP_LOCATION)

# TESTS_LOCATION = os.getcwd()
# TEMP_LOCATION = "C:\\Users\\james\\AppData\\Local\\Temp\\tmp6q_l1n1g"


print(os.getcwd())
req_folder = (project_dir / "requirements")

base_txt = (req_folder / "base.txt")
base_locked_txt = (req_folder / "base-locked.txt")
dev_txt = (req_folder / "dev.txt")
dev_locked_txt = (req_folder / "dev-locked.txt")
piper_file = (project_dir / "piper.json")
virtualenv_dir = (project_dir / ".virtualenvs" / "project_virtualenv")

# sys.path.append(".")
# sys.path.append("..")
from mrpiper import piper

try:
    command = 'code-insiders.cmd "{}"'.format(project_dir)
    # print(command)
    if (platform.system() == "Windows"):
        delegator.run(command, block=False)
except:
    pass


import errno
import stat
def handleRemoveReadonly(func, path, exc):
  excvalue = exc[1]
  if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
      func(path)
  else:
      pass

def create_test_project():
    temp_project_dir = tempfile.mkdtemp()

# def test_installing_itself():
#     with source_path:
#         c = delegator.run("piper add .")
#         print(c.out + c.err)
#         assert c.return_code == 0

def test_init():
    project_dir.chdir()
    piper.project._project_dir = None
    piper.project.detect_virtualenv_location()

    print(os.getcwd())
    print(piper.project.project_dir)
    piper.init(noinput=True, private=True)
    print(req_folder.abspath())
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
    assert "requests" in piper.project.piper_file["dependencies"]

    piper.add("Werkzeug")
    assert "Werkzeug" in base_txt.text()
    assert "werkzeug" in piper.project.piper_file["dependencies"]

    piper.add("regex")
    assert "regex" in base_txt.text()

    piper.remove("requests")
    piper.add("git+https://github.com/requests/requests.git@v2.18.4#egg=requests")
    assert "requests" in base_txt.text()

    if not (platform.system() == "Windows"):
        piper.add("git+https://github.com/scrapy/scrapy.git#egg=scrapy")
        assert "Scrapy" in base_txt.text()

    piper.add("path.py", dev=True)
    assert dev_txt.isfile()
    assert "path.py" in dev_txt.text()



def test_remove():
    piper.remove("requests")
    assert base_txt.isfile()
    assert not ("requests" in base_txt.text())
    assert not ("requests" in piper.project.piper_file["dependencies"])

    if not (platform.system() == "Windows"):
        piper.remove("scrapy")
        assert base_txt.isfile()
        assert not ("scrapy" in base_txt.text())

    piper.remove("path.py")
    assert dev_txt.isfile()
    assert not ("requests" in dev_txt.text())

    piper.remove("werkzeug")
    piper.remove("regex")

    lock = piper.project.piper_lock
    assert not lock["dependencies"].keys()
    assert not lock["dev_dependencies"].keys()
    assert not lock["dependables"]
    # assert not lock["frozen_deps"].keys() TODO: check this out

    piper_file = piper.project.piper_file
    assert not piper_file["dependencies"].keys()
    assert not piper_file["dev_dependencies"].keys()

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

    piper.upgrade("requests==2.0.0", upgrade_level="minor", noinput=True)
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

def test_why():
    piper.why("requests")

def test_install():
    piper.add("requests")
    piper.add("pytest", dev=True)
    piper.add("six")
    piper.add("coverage", dev=True)
    piper.project.virtualenv_dir.rmtree(ignore_errors=False, onerror=handleRemoveReadonly)
    piper.project.piper_lock_dir.remove_p()
    piper.project.piper_file_dir.remove_p()
    piper.install(dev=True)
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
    test_why()
    test_install()
