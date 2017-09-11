import click
from click.testing import CliRunner

from mrpiper import cli

runner = CliRunner()

def test_init():

    
    result = runner.invoke(cli.init, [])
    assert result.exit_code == 0
    # assert result.output == 'Hello Peter!\n'

def test_add():
    
    result = runner.invoke(cli.add, ["requests", "git+https://github.com/django/django.git#egg=django"])
    assert result.exit_code == 0
    assert "Package django installed" in result.output