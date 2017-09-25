import os

import parse
import delegator
from path import Path

def list_versions():
    # versions = Path("$PYENV_ROOT/versions/")
    PYENV_ROOT = os.environ.get("PYENV_ROOT")
    version_folder = Path("{}/versions/".format(PYENV_ROOT))
    return [item.name.__str__() for item in version_folder.dirs()]()

def set_local(version):
    c = delegator.run("pyenv local {}".format(version))
    return c.return_code == 0

def is_python_pyenv(filename):
    PYENV_ROOT = os.environ.get("PYENV_ROOT")
    if PYENV_ROOT:
        PYENV_ROOT = Path(PYENV_ROOT).abspath()
        return Path(filename).abspath().startswith(PYENV_ROOT)
    return False

def get_pyenv_version(python):
    c = delegator.run("{} --version".format(python))
    out = c.out + c.err
    out = out.replace("\n", "").replace("\r", "")
    # print(out)
    result = parse.parse("{}command exists in these Python versions: {}", out)
    # print(result)
    if result and result.fixed:
        return result.fixed[1].split()
    return []
