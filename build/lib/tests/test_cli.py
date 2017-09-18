# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import click
from click.testing import CliRunner
import delegator

import sys
sys.path.append(".")
sys.path.append("..")
from mrpiper import cli

import os
import tempfile
TEMP_LOCATION = tempfile.mkdtemp()
os.chdir(TEMP_LOCATION)

runner = CliRunner()

def test_init():
    delegator.run("piper init").return_code == 0
    # result = runner.invoke(cli.init, [])
    # print(result.output)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0

def test_add():
    delegator.run("piper add requests git+https://github.com/django/django.git@1.11.5#egg=django").return_code == 0
    delegator.run("piper add Werkzeug~=0.11.0").return_code == 0
    delegator.run("piper add pytest --dev").return_code == 0
    delegator.run("piper add coverage pytest --dev").return_code == 0

    # result = runner.invoke(cli.add, ["requests", "git+https://github.com/django/django.git@1.11.5#egg=django"])
    # print(result.output)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0
    # assert "Package django installed" in result.output

def test_remove():
    c = delegator.run("piper remove requests")
    # print(c.out + c.err)
    assert c.return_code == 0
    delegator.run("piper remove django").return_code == 0
    delegator.run("piper remove coverage pytest").return_code == 0
    # result = runner.invoke(cli.remove, ["requests"])
    # print(result.output)
    # print(result.exception)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0

def test_install():
    delegator.run("piper install").return_code == 0

def test_outdated():
    delegator.run("piper outdated").return_code == 0
    # result = runner.invoke(cli.outdated, [])
    # print(result.output)
    # print("exit_code:{}".format(result.exit_code))
    # assert result.exit_code == 0

def test_upgrade():
    delegator.run("piper upgrade --noinput Werkzeug").return_code == 0


if __name__=="__main__":
    test_init()
    test_add()
    test_remove()
    test_upgrade()
    test_outdated()
    test_install()
