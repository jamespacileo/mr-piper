Mr Piper (alpha) - Simple project package management
=====================================================

.. image:: https://img.shields.io/badge/Windows-supported!-brightgreen.svg

.. image:: https://img.shields.io/badge/Linux-supported!-brightgreen.svg

.. image:: https://img.shields.io/badge/MacOS-supported!-brightgreen.svg

Heavily inspired by Yarn, Piper offers a dead simple way to manage a project's dependencies (and more).

Piper uses pip and virtualenv under the hood, and (just like NPM and Yarn) always installs packages in a project isolated environment.

Piper makes it easy to make modules installable (and updatable) via a `piper.json` JSON file, instead of `setup.py`.


|image0| |image1| |image2| |image3| |image4| |Travis|

.. image:: https://i.imgur.com/QfiOH6z.gif

Why?
-----------

- No need to jump through countless hoops to get a test project going (with proper package management)
- Keep your environment nice and clean, with auto-removal of unnecessary components
- It's easy to make reproducible environments for your CI and deployments (no more "it-works-on-my-machine" syndrome)
- Easily make installable modules, no more `setup.py` fiddling
- Piper increases usefulness of some basic pip commands (e.g. check out `piper list`, `piper outdated`)
- A bunch of convenient utilities are included (e.g. `piper why`)


ROADMAP (PyconUK 2017 sprint):
------------

-  ⬜ Docs
-  ⬜ Store and use hashes in lock file
-  ⬜ Optional Pipfile support


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
