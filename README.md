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
```

## State of this plugin

Plugin is developed against mopidy version 2.0.1.

The following things are supported:

 * Browsing all artists/albums/tracks
 * Searching for any terms
 * Browsing playlists

The following things are **not** supported:

  * Creating, editing and deleting playlists
  * Searching explicitly for artists, albums, tracks, etc.
  * Subsonics smart playlists

## Contributors

The following people contributed to this project:
 - Frederick Gnodtke
