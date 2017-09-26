Mr Piper 🎻🐍 - Super simple project package manager
=====================================================

|windows| |linux| |macos|

|image0| |image1| |image2| |image3| |image4| |Travis|


---------------

Heavily inspired by `yarn <https://yarnpkg.com/en/docs/cli/>`_, Piper offers a dead simple way to manage a project's dependencies (and more).

Piper uses pip and virtualenv under the hood, and (just like NPM and Yarn) always installs packages in a project isolated environment.

Piper makes it easy to make modules installable (and updatable) via a `piper.json` JSON file, instead of fiddling with `setup.py`.



.. image:: https://i.imgur.com/QfiOH6z.gif

🤔 Why?
-----------

- No need to jump through countless hoops to get a test project going ☺️ (with proper package management)
- Keep your environment nice and clean ✨, with auto-removal of unnecessary components
- It's easy to make reproducible environments for your CI and deployments (no more "it-works-on-my-machine" syndrome)
- Easily make installable modules, no more :code:`setup.py` fiddling
- Piper increases usefulness of some basic pip commands (e.g. check out :code:`piper list`, :code:`piper outdated`)
- A bunch of convenient utilities are included (e.g. :code:`piper why`)
- Easy install from Github (e.g. :code:`piper add requests/requests`)
- Effortlessly keep your project version and git tags updated

------------

A star makes the developers happy 😊

|star-gif|

------------

Installation
------------

::

    $ pip install mr-piper

Usage
----------

Concise docs on usage and API going here

.. code::

        $ piper
        Usage: piper [OPTIONS] COMMAND [ARGS]...

        |  _____ _
        | |  __ (_)
        | | |__) | _ __   ___ _ __
        | |  ___/ | '_ \ / _ \ '__|
        | | |   | | |_) |  __/ |
        | |_|   |_| .__/ \___|_|
        |         | |
        |         |_|
        |

        Options:
        --help  Show this message and exit.

        Commands:
        add       Install and add a package to requirements
        info      info all installed packages
        init      Initialise project with virtual environment,...
        install   Install all packages in requirement files.
        list      List all installed packages
        outdated  Deletes virtualenv, requirements folder/files...
        remove    Remove a list of packages and their...
        upgrade   Upgrade a list of packages.
        why       Explain why a package exists
        wipe      Wipe virtualenv, requirements folder/files...

---------------

**Initialize project** :code:`piper init`

e.g. :code:`piper init --py 3.6 --outside`

Initializing a project creates:

- the PIP requirement files (base, dev and frozen lock files)
- the virtualenv (either outside or inside the project folder)
- a Piper file (where project information is stored)
- a Piper lock (where the reproducible working project configuration is stored)
- a working setup.py

.. image:: https://transfer.sh/34gGu/Hyper_2017-09-21_16-50-13.png

..
        $ piper init
        Initializing project
        Creating virtualenv...
        Virtualenv created ✓
        Your virtualenv path: /home/james/example_app/.virtualenvs/project_virtualenv
        Creating requirement files...
        Requirement files created ✓
        Creating piper file...
        Project name [example_app]: quick_example_project
        Author []: James Pacileo
        Version [0.0.1]: 0.0.1a1
        Description []: A quick example as demonstration
        Repository []:
        Licence []: MIT
        Is it a public project? [y/N]: y
        Piper file created ✓
        Creating piper lock...
        Piper lock created ✓

        ✨  Initialization complete

---------------

**Example piper.json**

.. code-block:: json

        {
            "created": "2017-09-20T21:10:07",
            "name": "mr-piper",
            "version": "0.1.3a2",
            "description": "The simple project package manager",
            "source_dir": "mrpiper",
            "repository": "https://github.com/jamespacileo/mr-piper",
            "author": "James Pacileo",
            "author_email": "",
            "keywords": "pip piper mrpiper package manager",
            "license": "MIT",
            "readme_filename": "README.rst",
            "py_modules": [
                "mrpiper.cli"
            ],
            "entry_points": {
                "console_scripts": [
                    "piper=mrpiper.cli:cli"
                ]
            },
            "classifiers": [
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.3",
                "Programming Language :: Python :: 3.4",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: Implementation :: CPython",
                "Programming Language :: Python :: Implementation :: PyPy"
            ],
            "data_files": [],
            "package_data": [],
            "exclude_packages": [],
            "dependencies": {
                "requests": "requests>=2.0.0",
                "path.py": "path.py>=10.4",
                "click": "click>=6.7",
                "click-log": "click-log>=0.2.0",
                "delegator.py": "delegator.py>=0.0.13",
                "future": "future>=0.16.0",
                "parse": "parse>=1.8.2",
                "semantic-version": "semantic-version>=2.6.0",
                "simplejson": "simplejson>=3.11.1",
                "tabulate": "tabulate>=0.7.7",
                "crayons": "crayons>=0.1.2",
                "click-spinner": "click-spinner>=0.1.7",
                "emoji": "emoji>=0.4.5"
            },
            "dev_dependencies": {
                "coverage": "coverage>=4.4.1",
                "coveralls": "coveralls>=1.2.0",
                "pytest": "pytest>=3.2.2"
            },
            "private": false
        }

---------------

**Install development packages** :code:`piper add`

e.g. :code:`piper add pytest --dev`

Dev only packages can be installed with the `--dev` option. These are automatically added to the dependencies and the lock is refreshed.

.. image:: https://transfer.sh/zXigS/Hyper_2017-09-21_16-51-27.png

..
        $ piper add pytest coverage --dev
        Installing pytest...
        ...
        Package pytest installed ✓
        Requirements locked ✓
        Requirements updated ✓

        Installing coverage...
        ...
        Package coverage installed ✓
        Requirements locked ✓
        Requirements updated ✓

        ✨  Adding package complete

---------------

**Install a package from github** :code:`piper add username/project@tag`

e.g. :code:`piper add django/django@1.11.5`

Easy install of python modules stored on Github.

.. image:: https://transfer.sh/U6ReQ/Hyper_2017-09-21_16-52-31.png

..
        $ piper add requests/requests
        Installing requests/requests...
        requests/requests resolved as git+https://github.com/requests/requests.git#egg=requests
        ...
        Package requests installed ✓
        Requirements locked ✓
        Requirements updated ✓

        ✨  Adding package complete

---------------

**Removing a package** :code:`piper remove`

e.g. :code:`piper remove django`

Remove a package and all safely deletable sub-dependencies, for a sparkly clean environment.

.. image:: https://transfer.sh/MpUXN/Hyper_2017-09-21_16-53-00.png

..
        $ piper remove requests
        Removing package requests...
        Uninstalling certifi-2017.7.27.1:
        Successfully uninstalled certifi-2017.7.27.1
        Uninstalling chardet-3.0.4:
        Successfully uninstalled chardet-3.0.4
        Uninstalling idna-2.6:
        Successfully uninstalled idna-2.6
        Uninstalling urllib3-1.22:
        Successfully uninstalled urllib3-1.22
        Uninstalling requests-2.18.4:
        Successfully uninstalled requests-2.18.4
        Package requests removed ✓
        Packaged locked ✓
        Requirement files updated ✓

        ✨  Package removal complete

---------------

**Install all dependencies (uses lock by default)** :code:`piper install`

e.g. :code:`piper install --dev`

Install (or reinstall) dependencies specified in the requirements. It uses the locked dependencies by default to guarantee a working version.

.. image:: https://transfer.sh/G8QRZ/Hyper_2017-09-21_19-37-38.png

---------------

**Find outdated packages** :code:`piper outdated`

e.g. :code:`piper outdated --all`


.. image:: https://transfer.sh/3gfBu/Hyper_2017-09-21_17-02-56.png

..
        $ piper outdated --all
        Fetching outdated packages...
        Name      Current    Wanted    Latest
        --------  ---------  --------  --------
        requests  2.0.0      2.0.0     2.18.4
        py        1.4.34     1.4.34    1.4.34
        pytest    3.2.2      3.2.2     3.2.2
        coverage  4.4.1      4.4.1     4.4.1
        Werkzeug  0.9.6      0.9.6     0.12.2

---------------

**List project's package structure** :code:`piper list`

e.g. :code:`piper list`


.. image:: https://transfer.sh/TYZGX/Hyper_2017-09-21_16-57-49.png

..
        $ piper list
        # base = green | dev = magenta | sub dependencies = cyan
        ├─ pytest==3.2.2
        │  └─ setuptools
        │  └─ py>=1.4.33
        ├─ py==1.4.34
        ├─ Werkzeug==0.9.6
        ├─ coverage==4.4.1
        ├─ requests==2.0.0


---------------

**Update porject version (and git tag)** :code:`piper version`

e.g. :code:`piper version -y`

Easily check and update the project's version, with the option ability to add a git tag version.

.. image:: https://transfer.sh/gyhnV/Hyper_2017-09-21_19-22-24.png

---------------

**Why does a package exist** :code:`piper why`

e.g. :code:`piper why idna`

Check why a package is installed.

.. image:: https://transfer.sh/CCLhh/Hyper_2017-09-21_19-44-55.png

---------------

**Get virtualenv activate command** :code:`piper activate`

e.g. :code:`piper activate`

Returns the shell command used to activate the virtualenv

.. image:: https://transfer.sh/JKnuk/Hyper_2017-09-21_20-27-12.png

---------------

Concise docs on usage and API going here


Current TODO
-------------

-  ⬜ Complete basic docs
-  ⬜ Prune and cleanup code
-  ⬜ Add a few more tests
-  ⬜ 90%+ test coverage

Planned CLI APIs
-----------------

- :code:`piper shell` - Spawn a shell where the virtualenv is activated
- :code:`piper build` - Build distributable package from project
- :code:`piper publish --build` - Build and publish project on PyPI (or other index)
- :code:`piper run command` - Run custom command (inspired by npm/yarn commands)
- :code:`piper licenses` - List all dependency licences
- :code:`piper config` - To store user global settings for Piper's behavior

ROADMAP (PyconUK 2017 sprint):
------------

This list is undergoing changes.

-  ⬜ Improve documentation
-  ⬜ Prune some dependencies used
-  ⬜ Integrate packages hashes
-  ⬜ Easy way to add setup.py commands (e.g. packaga.json scripts)
-  ⬜ Custom virtualenv location
-  ⬜ Optional: Pipfile support


.. |windows| image:: https://img.shields.io/badge/Windows-supported-brightgreen.svg
.. |linux| image:: https://img.shields.io/badge/Linux-supported-brightgreen.svg
.. |macos| image:: https://img.shields.io/badge/MacOS-supported-brightgreen.svg


.. |image0| image:: https://img.shields.io/pypi/v/mr-piper.svg
   :target: https://pypi.python.org/pypi/mr-piper
.. |image1| image:: https://img.shields.io/pypi/l/mr-piper.svg
   :target: https://pypi.python.org/pypi/mr-piper
.. |image2| image:: https://img.shields.io/pypi/wheel/mr-piper.svg
   :target: https://pypi.python.org/pypi/mr-piper
.. |image3| image:: https://img.shields.io/pypi/pyversions/mr-piper.svg
   :target: https://pypi.python.org/pypi/mr-piper
.. |image4| image:: https://img.shields.io/appveyor/ci/jamespacileo/mr-piper.svg
   :target: https://ci.appveyor.com/project/jamespacileo/mr-piper/branch/master
.. |Travis| image:: https://img.shields.io/travis/rust-lang/rust.svg
   :target: https://travis-ci.org/jamespacileo/mr-piper

.. |star-gif| image:: https://transfer.sh/CsffY/2017-09-25_16-51-28.gif
   :target: https://github.com/jamespacileo/mr-piper
