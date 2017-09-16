import os
import sys
import tempfile

from path import path
from mrpiper import piper

# sys.path.append(0, os.path.join(".."))


TESTS_LOCATION = os.getcwd()
TEMP_LOCATION = tempfile.mkdtemp()
project_dir = path(TEMP_LOCATION)
project_dir.chdir()
req_folder = (project_dir / "requirements")

base_txt = (req_folder / "base.txt")
base_locked_txt = (req_folder / "base-locked.txt")
dev_txt = (req_folder / "dev.txt")
dev_locked_txt = (req_folder / "dev-locked.txt")

def create_test_project():
    temp_project_dir = tempfile.mkdtemp()
    

def test_init():
    piper.init()
    assert req_folder.exists()
    assert base_txt.exists()
    assert base_locked_txt.exists()
    assert dev_txt.exists()
    assert dev_locked_txt.exists()

def test_add():
    piper.add("requests")
    assert base_txt.isfile()
    assert "requests" in base_txt.text()

    piper.add("path.py", dev=True)
    assert dev_txt.isfile()
    assert "path.py" in dev_txt.text()

def test_remove():
    pass

def test_install():
    pass