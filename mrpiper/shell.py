# encoding: utf-8

import sys
import signal

if sys.version_info < (3, 3):
    from backports.shutil_get_terminal_size import get_terminal_size
else:
    from shutil import get_terminal_size

import pexpect
import click
import crayons

def activate_virtualenv(project, source=True):
    """Returns the string to activate a virtualenv."""

    # Suffix for other shells.
    suffix = ''

    # # Support for fish shell.
    # if 'fish' in PIPENV_SHELL:
    #     suffix = '.fish'

    # # Support for csh shell.
    # if 'csh' in PIPENV_SHELL:
    #     suffix = '.csh'

    # Escape any spaces located within the virtualenv path to allow
    # for proper activation.
    venv_location = project.virtualenv_location.replace(' ', r'\ ')

    if source:
        return 'source {0}/bin/activate{1}'.format(venv_location, suffix)
    else:
        return '{0}/bin/activate'.format(venv_location)


def do_activate_virtualenv(project, bare=False):
    """Executes the activate virtualenv functionality."""
    # Check for environment marker, and skip if it's set.
    if 'PIPENV_ACTIVE' not in os.environ:
        if not bare:
            click.echo('To activate this project\'s virtualenv, run the following:\n $ {0}'.format(
                crayons.red('pipenv shell'))
            )
        else:
            click.echo(activate_virtualenv(project))

def do_shell(project, python, compat=False):

    cmd = 'virtualenv'
    # args = [project.virtualenv_name]
    args = []


    # Grab current terminal dimensions to replace the hardcoded default
    # dimensions of pexpect
    terminal_dimensions = get_terminal_size()

    try:
        c = pexpect.spawn(
            cmd,
            args,
            dimensions=(
                terminal_dimensions.lines,
                terminal_dimensions.columns
            )
        )

    # Windows!
    except AttributeError:
        import subprocess
        p = subprocess.Popen([cmd] + list(args), shell=True, universal_newlines=True)
        p.communicate()
        sys.exit(p.returncode)

    # Activate the virtualenv if in compatibility mode.
    if compat:
        c.sendline(activate_virtualenv(project))

    # Send additional arguments to the subshell.
    # if shell_args:
    #     c.sendline(' '.join(shell_args))

    # Handler for terminal resizing events
    # Must be defined here to have the shell process in its context, since we
    # can't pass it as an argument
    def sigwinch_passthrough(sig, data):
        terminal_dimensions = get_terminal_size()
        c.setwinsize(terminal_dimensions.lines, terminal_dimensions.columns)
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)

    # Interact with the new shell.
    c.interact(escape_character=None)
    c.close()
    sys.exit(c.exitstatus)
