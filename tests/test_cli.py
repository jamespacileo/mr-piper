# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import click
# from click.testing import CliRunner
import delegator
import json
from path import Path

import sys
sys.path.append(".")
sys.path.append("..")
from mrpiper import cli

import os
import tempfile
TEMP_LOCATION = tempfile.mkdtemp()
os.chdir(TEMP_LOCATION)

# TEMP_LOCATION = (Path("temp") / "cli_testing_project")
# Path("temp").mkdir_p()
# TEMP_LOCATION.rmtree_p()
# TEMP_LOCATION.mkdir_p()
# os.chdir(TEMP_LOCATION)
PROJECT_DIR = Path(".")
# runner = CliRunner()
try:
    command = 'code-insiders.cmd "{}"'.format(PROJECT_DIR)
    # print(command)
    if (platform.system() == "Windows"):
        delegator.run(command, block=False)
except:
    pass

def test_init():
    print("Testing init...")
    c = delegator.run("piper init --yes")
    print(c.out + c.err)
    assert c.return_code == 0
    # print((PROJECT_DIR / "piper.lock").abspath())
    assert (PROJECT_DIR / "piper.lock").isfile()
    assert (PROJECT_DIR / "piper.json").isfile()
    assert (PROJECT_DIR / ".virtualenvs").exists()
    assert (PROJECT_DIR / "requirements").exists()
    # result = runner.invoke(cli.init, [])
    # print(result.output)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0

def test_add():
    print("Testing add...")
    delegator.run("piper add requests git+https://github.com/django/django.git@1.11.5#egg=django").return_code == 0
    delegator.run("piper add Werkzeug~=0.11.0").return_code == 0
    delegator.run("piper add pytest --dev").return_code == 0
    delegator.run("piper add coverage pytest --dev").return_code == 0

    delegator.run("piper add https://github.com/requests/requests/archive/master.zip").return_code == 0
    delegator.run("git clone https://github.com/requests/requests.git temp_requests").return_code == 0
    delegator.run("piper add ./temp_requests/").return_code == 0

    # result = runner.invoke(cli.add, ["requests", "git+https://github.com/django/django.git@1.11.5#egg=django"])
    # print(result.output)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0
    # assert "Package django installed" in result.output

def test_remove():
    print("Testing remove...")
    c = delegator.run("piper remove requests")
    print(c.out + c.err)
    assert c.return_code == 0
    delegator.run("piper remove django").return_code == 0
    delegator.run("piper remove coverage pytest").return_code == 0
    # result = runner.invoke(cli.remove, ["requests"])
    # print(result.output)
    # print(result.exception)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0

def test_outdated():
    print("Testing outdated...")
    delegator.run("piper add requests==2.0.0").return_code == 0
    delegator.run("piper add boto~=2.0.0").return_code == 0
    delegator.run("piper add simplejson~=2.0").return_code == 0
    delegator.run("piper add node~=0.1").return_code == 0
    c = delegator.run("piper outdated --json")
    assert c.return_code == 0
    print(c.out)
    data = json.loads(c.out)
    assert len(data) > 0
    # result = runner.invoke(cli.outdated, [])
    # print(result.output)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0

def test_upgrade():
    print("Testing upgrade...")
    delegator.run("piper upgrade --noinput requests").return_code == 0

def test_why():
    print("Testing why...")
    delegator.run("piper add requests").return_code == 0
    c = delegator.run("piper why requests")
    assert c.return_code == 0
    assert "dependencies" in c.out

    delegator.run("piper add pytest").return_code == 0
    c = delegator.run("piper why pytest")
    assert c.return_code == 0
    assert "devDpendencies" in c.out

def test_install():
    print("Testing install...")
    delegator.run("piper install").return_code == 0


if __name__=="__main__":
    test_init()
    # test_add()
    # test_remove()
    test_outdated()
    test_upgrade()
    # test_install()
