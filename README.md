Mr Piper - Simple project package management
-------------


[![](https://img.shields.io/pypi/v/mrpiper.svg)](https://pypi.python.org/pypi/mrpiper)
[![](https://img.shields.io/pypi/l/mrpiper.svg)](https://pypi.python.org/pypi/mrpiper)
[![](https://img.shields.io/pypi/wheel/mrpiper.svg)](https://pypi.python.org/pypi/mrpiper)
[![](https://img.shields.io/pypi/pyversions/mrpiper.svg)](https://pypi.python.org/pypi/mrpiper)
[![](https://img.shields.io/appveyor/ci/jamespacileo/mr-piper.svg)](https://ci.appveyor.com/project/jamespacileo/mr-piper/branch/master)
[![Travis](https://img.shields.io/travis/rust-lang/rust.svg)](https://travis-ci.org/jamespacileo/mr-piper)
[![Coverage Status](https://coveralls.io/repos/github/jamespacileo/mr-piper/badge.svg?branch=master)](https://coveralls.io/github/jamespacileo/mr-piper?branch=master)

### TODO:

- [X] Publish bare bones prototype
- [X] 🏃 `piper init` working as expected
    - [ ] 🏃 add specific python version option eg `--py2`, `--py3`, `--py3.4`
    - [ ] 🏃 add `--global` option, for skipping virtualenv
    - [ ] 🏃 add `--inside` and `--outside` for defining where you want the virtualenv to be (inside or outside the project folder)
    - [ ] 🏃 custom virtualenv location
- [X] 🏃 `piper add` working as expected
- [X] 🏃 `piper remove` working as expected
- [X] 🏃 `piper outdated` working as expected
- [X] 🏃 Enable both `--no-input` and `version selection` for `piper upgrade`
- [X] 🏃 `piper upgrade` working as expected
- [ ] 🏃 `piper install` working as expected
    - [ ] 🏃 import from existing requirements file
- [ ] 🏃 Adjust module requirements
- [ ] 🏃 CLI autocomplete
- [X] 🏃 Python 2 and 3 compatibility
- [ ] 🏃 Unit tests for CLI
- [X] 🏃 Unit tests for Piper module
- [X] 🏃 Test coverage calculation and Coveralls integration
- [ ] 🏃 Friendly Github installs eg `piper add django/django`
- [ ] Refine `piper.json` file
- [ ] Solidify module's setup.py
- [ ] Linting and PEP8
- [ ] Check if PIP, Virtualenv need to be installed/updated and warn user
- [ ] Integrate with Travis CI
- [ ] Integrate with AppVeyor
- [ ] Add build + other live chips on README
- [ ] Deploy working module to PyPI
- [ ] Use MrPiper with MrPiper
- [ ] Create minimum API docs in README
- [ ] Create working examples
- [ ] Pipfile compatibility
- [ ] Documentation
- [ ] Pipfile compatibility
- [ ] Add additional dependency types
- [ ] Hashes

*Please raise an issue to add features*

### Following are old docs - please ignore for the time being

Making Python dependencies management a joy.

    nest init

Initialize Python project. Add requirements folder, add nest lock file, add setup.py.

    nest install

Install all dependencies. Add `--dev` or `--local` for *development dependencies*. Add `--prod` for *production dependencies*.

    nest add <package>

Find and current package version to requirements.
Dependencies are added to freeze.
Add `--prod` if only a production dependency. Add `--local` or `--dev` if a development dependency.

    nest remove <package>

Uninstalls package with all non conflicting dependencies. Removes package from requirements file and frozen files.

    nest publish

Publish package to PYPI
