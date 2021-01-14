*************
Mopidy-Subidy
*************

.. image:: https://img.shields.io/pypi/v/Mopidy-Subidy
    :target: https://pypi.org/project/Mopidy-Subidy/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/Prior99/mopidy-subidy
    :target: https://circleci.com/gh/Prior99/mopidy-subidy
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/Prior99/mopidy-subidy
    :target: https://codecov.io/gh/Prior99/mopidy-subidy
    :alt: Test coverage

**This library is actively looking for maintainers to help out as I do not have the time or need to maintain this anymore. Please contact me if you feel that you could maintain this.**

A Subsonic backend for Mopidy using `py-sonic
<https://github.com/crustymonkey/py-sonic>`_.


Installation
============

Install the latest release from PyPI by running::

    python3 -m pip install Mopidy-Subidy

Install the development version directly from this repo by running::

    python3 -m pip install https://github.com/Prior99/mopidy-subidy/archive/master.zip

See https://mopidy.com/ext/subidy/ for alternative installation methods.


Configuration
=============

Before starting Mopidy, you must add configuration for Mopidy-Subidy to your
Mopidy configuration file::

   [subidy]
   url=https://path.to/your/subsonic/server
   username=subsonic_username
   password=your_secret_password

In addition, the following optional configuration values are supported:

- ``enabled`` -- Defaults to ``true``. Set to ``false`` to disable the
  extension.

- ``legacy_auth`` -- Defaults to ``false``. Setting to ``true`` may solve some
  connection errors.

- ``api_version`` -- Defaults to ``1.14.0``, which is the version used by
  Subsonic 6.2.


State of this plugin
====================

The following things are supported:

- Browsing all artists/albums/tracks
- Searching for any terms
- Browsing, creating, editing and deleting playlists
- Searching explicitly for one of: artists, albums, tracks

The following things are **not** supported:

- Subsonic's smart playlists
- Searching for a combination of filters (artist and album, artist and track, etc.)


Credits
=======

- Original author: `Frederick Gnodtke <https://github.com/Prior99>`__
- Current maintainer: `Frederick Gnodtke <https://github.com/Prior99>`__
- `Contributors <https://github.com/Prior99/mopidy-subidy/graphs/contributors>`_
