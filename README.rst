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
