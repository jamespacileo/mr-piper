import os
import sys
import tempfile
import delegator

from path import Path

# sys.path.append(os.path.join(os.path.abspath(__file__), ".."))
# print(os.path.join(os.path.realpath(__file__), ".."))
sys.path.append(".")
sys.path.append("..")
from mrpiper import piper


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
    delegator.run(command, block=False)
except:
    pass

def create_test_project():
    temp_project_dir = tempfile.mkdtemp()

    

def test_init():
    piper.init()
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
    
    piper.add("git+https://github.com/scrapy/scrapy.git#egg=scrapy")
    assert base_txt.isfile()
    assert "scrapy" in base_txt.text()

    piper.add("path.py", dev=True)
    assert dev_txt.isfile()
    assert "path.py" in dev_txt.text()



def test_remove():
    piper.remove("requests")
    assert base_txt.isfile()
    assert not ("requests" in base_txt.text())
    
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
    piper.upgrade("requests", patch=True)
    assert ("requests==2.0.1" in dev_txt.text())

    piper.add("requests==1.0.0", dev=True)
    piper.upgrade("requests", patch=True)
    assert ("requests==1.0.4" in dev_txt.text())
    piper.upgrade("requests", minor=True)
    assert ("requests==1.2.3" in dev_txt.text())
    piper.upgrade("requests", major=True)
    assert ("requests==2." in dev_txt.text())
    piper.upgrade("requests<2.0.0", major=True)
    assert ("requests==1.2.3" in dev_txt.text())

    # Check warning for editables

    # Version selection



def test_outdated():
    piper.add("requests==2.16.0", dev=True)
    # piper.add("pytest", dev=True)
    # piper.upgrade("requests", patch=True)
    assert ("requests" in dev_txt.text())
    piper.outdated(all_pkgs=True, verbose=True)


def test_install():
    pass

if __name__=="__main__":
    test_init()
    # test_add()
    # test_remove()
    # test_upgrade()
    test_outdated()