Mr Piper (alpha) - Simple project package management
----------------------------------------------------

|image0| |image1| |image2| |image3| |image4| |Travis|

.. image:: https://i.imgur.com/bKWITFN.gifv

TODO:
~~~~~

-  [X] Publish bare bones prototype
-  [X] 🏃 ``piper init`` working as expected

   -  [ ] 🏃 add specific python version option eg ``--py2``, ``--py3``,
      ``--py3.4``
   -  [ ] 🏃 add ``--global`` option, for skipping virtualenv
   -  [ ] 🏃 add ``--inside`` and ``--outside`` for defining where you
      want the virtualenv to be (inside or outside the project folder)
   -  [ ] 🏃 custom virtualenv location

-  [X] 🏃 ``piper add`` working as expected
-  [X] 🏃 ``piper remove`` working as expected

   -  [ ] add confirmation prompt

-  [X] 🏃 ``piper outdated`` working as expected

   -  [ ] add ``--format json`` option

-  [X] 🏃 Enable both ``--no-input`` and ``version selection`` for
   ``piper upgrade``
-  [X] 🏃 ``piper upgrade`` working as expected
-  [X] 🏃 ``piper install`` working as expected

   -  [ ] 🏃 import from existing requirements file

-  [ ] 🏃 Adjust module requirements
-  [ ] 🏃 CLI autocomplete
-  [X] 🏃 Python 2 and 3 compatibility
-  [ ] 🏃 Unit tests for CLI
-  [X] 🏃 Unit tests for Piper module
-  [X] 🏃 Test coverage calculation and Coveralls integration
-  [ ] 🏃 Friendly Github installs eg ``piper add django/django``
-  [ ] Refine ``piper.json`` file
-  [ ] Solidify module’s setup.py
-  [ ] Linting and PEP8
-  [ ] Check if PIP, Virtualenv need to be installed/updated and warn
   user
-  [X] Integrate with Travis CI
-  [X] Integrate with AppVeyor
-  [X] Add build + other live chips on README
-  [ ] Deploy working module to PyPI
-  [ ] Use MrPiper with MrPiper
-  [ ] Create minimum API docs in README
-  [ ] Create working examples
-  [ ] Pipfile compatibility
-  [ ] Documentation
-  [ ] Pipfile compatibility
-  [ ] Add additional dependency types
-  [ ] Hashes

*Please raise an issue to add features*

Following are old docs - please ignore for the time being
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Making Python dependencies management a joy.

::

    nest init

Initialize Python project. Add requirements folder, add nest lock file,
add setup.py.

::

    nest install

Install all dependencies. Add ``--dev`` or ``--local`` for *development
dependencies*. Add ``--prod`` for *production dependencies*.

::

    nest add <package>

Find and current package version to requirements. Dependencies are added
to freeze. A

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
