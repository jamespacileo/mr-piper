The Python NEST
-------------

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
