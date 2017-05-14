# Mopidy Subidy

A subsonic backend for mopidy using [py-sub](https://github.com/crustymonkey/py-sonic).

## Configuration

Add a section similiar to the following to your mopidy configuration:

```ini
[subidy]
enabled=True
url=https://path.to/your/subsonic/server
username=subsonic_username
password=your_secret_password
legacy_auth=(optional - setting to yes may solve some connection errors)
api_version=(optional - specify which API version to use. Subsonic 6.2 uses 1.14.0)
```

## State of this plugin

Plugin is developed against mopidy version 2.0.1.

The following things are supported:

 * Browsing all artists/albums/tracks
 * Searching for any terms
 * Browsing playlists
 * Searching explicitly for one of: artists, albums, tracks

The following things are **not** supported:

  * Creating, editing and deleting playlists
  * Subsonics smart playlists
  * Searching for a combination of filters (artist and album, artist and track, etc.)

## Contributors

The following people contributed to this project:
 - Frederick Gnodtke
 - hhm0
