# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import click
from click.testing import CliRunner

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
    result = runner.invoke(cli.init, [])
    print(result.output)
    print("exit_code:{}".format(result.exit_code))
    assert result.exit_code == 0

def test_add():
    result = runner.invoke(cli.add, ["requests", "git+https://github.com/django/django.git@1.11.5#egg=django"])
    print(result.output)
    print("exit_code:{}".format(result.exit_code))
    assert result.exit_code == 0
    assert "Package django installed" in result.output

def test_remove():
    result = runner.invoke(cli.remove, ["requests"])
    print(result.output)
    print("exit_code:{}".format(result.exit_code))
    assert result.exit_code == 0

def test_install():
    pass

def test_outdated():
    result = runner.invoke(cli.outdated, [])
    print(result.output)
    print("exit_code:{}".format(result.exit_code))
    assert result.exit_code == 0

def test_upgrade():
    pass


if __name__=="__main__":
    test_init()
    test_add()
    test_remove()
    test_upgrade()
    test_outdated()
    test_install()
