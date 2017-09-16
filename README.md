Mr Piper - Simple project package management
-------------

### TODO:

- [X] Publish bare bones prototype
- [X] 🏃 `piper init` working as expected
- [ ] 🏃 `piper add` working as expected
- [ ] 🏃 `piper remove` working as expected
- [ ] 🏃 `piper outdated` working as expected
- [ ] 🏃 `piper upgrade` working as expected
- [ ] 🏃 Python 2 and 3 compatibility
- [ ] 🏃 Unit tests for CLI
- [ ] 🏃 Unit tests for Piper module
- [ ] Refine `piper.json` file
- [ ] Solidify module's setup.py
- [ ] Linting and PEP8
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
