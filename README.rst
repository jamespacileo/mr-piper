Mr Piper (alpha) 🎻🐍 - Simple project package management
=====================================================

|windows| |linux| |macos|

|image0| |image1| |image2| |image3| |image4| |Travis|

---------------

Heavily inspired by `yarn <https://yarnpkg.com/en/docs/cli/>`_, Piper offers a dead simple way to manage a project's dependencies (and more).

Piper uses pip and virtualenv under the hood, and (just like NPM and Yarn) always installs packages in a project isolated environment.

Piper makes it easy to make modules installable (and updatable) via a `piper.json` JSON file, instead of `setup.py`.



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

Initialize project
///////////////////

.. code::

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

Install development packages
/////////////////////////////

.. code::

        $ piper add pytest coverage --dev
        Installing pytest...
        Collecting pytest
        Using cached pytest-3.2.2-py2.py3-none-any.whl
        Requirement already satisfied: setuptools in ./.virtualenvs/project_virtualenv/lib/python2.7/site-packages (from pytest)
        Collecting py>=1.4.33 (from pytest)
        Using cached py-1.4.34-py2.py3-none-any.whl
        Installing collected packages: py, pytest
        Successfully installed py-1.4.34 pytest-3.2.2
        Package pytest installed ✓
        Requirements locked ✓
        Requirements updated ✓

        Installing coverage...
        Collecting coverage
        Using cached coverage-4.4.1-cp27-cp27mu-manylinux1_x86_64.whl
        Installing collected packages: coverage
        Successfully installed coverage-4.4.1
        Package coverage installed ✓
        Requirements locked ✓
        Requirements updated ✓

        ✨  Adding package complete

Install a package from github
//////////////////////////////

.. code::

        $ piper add requests/requests
        Installing requests/requests...
        requests/requests resolved as git+https://github.com/requests/requests.git#egg=requests
        Obtaining requests from git+https://github.com/requests/requests.git#egg=requests
        Cloning https://github.com/requests/requests.git to ./.virtualenvs/project_virtualenv/src/requests
        Collecting chardet<3.1.0,>=3.0.2 (from requests)
        Using cached chardet-3.0.4-py2.py3-none-any.whl
        Collecting idna<2.7,>=2.5 (from requests)
        Using cached idna-2.6-py2.py3-none-any.whl
        Collecting urllib3<1.23,>=1.21.1 (from requests)
        Using cached urllib3-1.22-py2.py3-none-any.whl
        Collecting certifi>=2017.4.17 (from requests)
        Using cached certifi-2017.7.27.1-py2.py3-none-any.whl
        Installing collected packages: chardet, idna, urllib3, certifi, requests
        Running setup.py develop for requests
        Successfully installed certifi-2017.7.27.1 chardet-3.0.4 idna-2.6 requests urllib3-1.22
        Package requests installed ✓
        Requirements locked ✓
        Requirements updated ✓

        ✨  Adding package complete

Concise docs on usage and API going here


Current TODO
-------------

-  ⬜ Complete basic docs
-  ⬜ Prune and cleanup code
-  ⬜ Add a few more tests
-  ⬜ 90%+ test coverage

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


.. |image0| image:: https://img.shields.io/pypi/v/mrpiper.svg
   :target: https://pypi.python.org/pypi/mrpiper
.. |image1| image:: https://img.shields.io/pypi/l/mrpiper.svg
   :target: https://pypi.python.org/pypi/mrpiper
.. |image2| image:: https://img.shields.io/pypi/wheel/mrpiper.svg
   :target: https://pypi.python.org/pypi/mrpiper
.. |image3| image:: https://img.shields.io/pypi/pyversions/mrpiper.svg
   :target: https://pypi.python.org/pypi/mrpiper
.. |image4| image:: https://img.shields.io/appveyor/ci/jamespacileo/mr-piper.svg
   :target: https://ci.appveyor.com/project/jamespacileo/mr-piper/branch/master
.. |Travis| image:: https://img.shields.io/travis/rust-lang/rust.svg
   :target: https://travis-ci.org/jamespacileo/mr-piper
