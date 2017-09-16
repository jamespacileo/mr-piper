import os
import sys
import tempfile
import delegator

from path import path

# sys.path.append(os.path.join(os.path.abspath(__file__), ".."))
# print(os.path.join(os.path.realpath(__file__), ".."))
sys.path.append(".")
from mrpiper import piper


TESTS_LOCATION = os.getcwd()
TEMP_LOCATION = tempfile.mkdtemp()
project_dir = path(TEMP_LOCATION)
project_dir.chdir()
req_folder = (project_dir / "requirements")

base_txt = (req_folder / "base.txt")
base_locked_txt = (req_folder / "base-locked.txt")
dev_txt = (req_folder / "dev.txt")
dev_locked_txt = (req_folder / "dev-locked.txt")
piper_file = (project_dir / "piper.json")
virtualenv_dir = (project_dir / ".virtualenvs" / "project_virtualenv")
delegator.run('explorer /select,"{}"'.format(project_dir), block=False)

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

    piper.add("path.py", dev=True)
    assert dev_txt.isfile()
    assert "path.py" in dev_txt.text()

def test_remove():
    piper.remove("requests")
    assert base_txt.isfile()
    assert not ("requests" in base_txt.text())
    
    piper.remove("path")
    assert base_txt.isfile()
    assert not ("requests" in dev_txt.text())


def test_install():
    pass

if __name__=="__main__":
    test_init()
    test_add()
    test_remove()