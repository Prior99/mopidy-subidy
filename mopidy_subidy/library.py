from mopidy import backend, models
from mopidy.models import Ref, SearchResult
from mopidy_subidy import uri

import logging
logger = logging.getLogger(__name__)

class SubidyLibraryProvider(backend.LibraryProvider):
    def __create_vdirs():
        vdir_templates = [
            dict(id="root", name="Subsonic"),
            dict(id="artists", name="Artists"),
            dict(id="albums", name="Albums"),
            dict(id="rootdirs", name="Directories"),
        ]
        # Create a dict with the keys being the `id`s in `vdir_templates`
        # and the values being objects containing the vdir `id`,
        # the human readable name as `name`, and the URI as `uri`.
        vdirs = {}
        for template in vdir_templates:
            vdir = template.copy()
            vdir.update(uri=uri.get_vdir_uri(vdir["id"]))
            vdirs[template['id']] = vdir
        return vdirs

    _vdirs = __create_vdirs()

    def __raw_vdir_to_ref(vdir):
        if vdir is None:
            return None
        return Ref.directory(
            name=vdir['name'],
            uri=vdir['uri'])

    root_directory = __raw_vdir_to_ref(_vdirs['root'])

    _raw_vdir_to_ref = staticmethod(__raw_vdir_to_ref)

    def __init__(self, *args, **kwargs):
        super(SubidyLibraryProvider, self).__init__(*args, **kwargs)
        self.subsonic_api = self.backend.subsonic_api

    def browse_songs(self, album_id):
        return self.subsonic_api.get_songs_as_refs(album_id)

    def browse_albums(self, artist_id=None):
        return self.subsonic_api.get_albums_as_refs(artist_id)

    def browse_artists(self):
        return self.subsonic_api.get_artists_as_refs()

    def browse_rootdirs(self):
        return self.subsonic_api.get_rootdirs_as_refs()

    def browse_diritems(self, directory_id):
        return self.subsonic_api.get_diritems_as_refs(directory_id)

    def lookup_song(self, song_id):
        song = self.subsonic_api.get_song_by_id(song_id)
        if song is None:
            return []
        else:
            return [song]

    def lookup_album(self, album_id):
        return self.subsonic_api.get_songs_as_tracks(album_id)

    def lookup_artist(self, artist_id):
        return list(self.subsonic_api.get_artist_as_songs_as_tracks_iter(artist_id))

    def lookup_directory(self, directory_id):
        return list(self.subsonic_api.get_recursive_dir_as_songs_as_tracks_iter(directory_id))

    def lookup_playlist(self, playlist_id):
        return self.subsonic_api.get_playlist_as_playlist(playlist_id).tracks

    def browse(self, browse_uri):
        if browse_uri == uri.get_vdir_uri('root'):
            root_vdir_names = ["rootdirs", "artists", "albums"]
            root_vdirs = [self._vdirs[vdir_name] for vdir_name in root_vdir_names]
            sorted_root_vdirs = sorted(root_vdirs, key=lambda vdir: vdir["name"])
            return [self._raw_vdir_to_ref(vdir) for vdir in sorted_root_vdirs]
        elif browse_uri == uri.get_vdir_uri("rootdirs"):
            return self.browse_rootdirs()
        elif browse_uri == uri.get_vdir_uri("artists"):
            return self.browse_artists()
        elif browse_uri == uri.get_vdir_uri("albums"):
            return self.browse_albums()
        else:
            uri_type = uri.get_type(browse_uri)
            if uri_type == uri.DIRECTORY:
                return self.browse_diritems(uri.get_directory_id(browse_uri))
            elif uri_type == uri.ARTIST:
                return self.browse_albums(uri.get_artist_id(browse_uri))
            elif uri_type == uri.ALBUM:
                return self.browse_songs(uri.get_album_id(browse_uri))
            else:
                return []

    def lookup_one(self, lookup_uri):
        type = uri.get_type(lookup_uri)
        if type == uri.ARTIST:
            return self.lookup_artist(uri.get_artist_id(lookup_uri))
        if type == uri.ALBUM:
            return self.lookup_album(uri.get_album_id(lookup_uri))
        if type == uri.DIRECTORY:
            return self.lookup_directory(uri.get_directory_id(lookup_uri))
        if type == uri.SONG:
            return self.lookup_song(uri.get_song_id(lookup_uri))
        if type == uri.PLAYLIST:
            return self.lookup_playlist(uri.get_playlist_id(lookup_uri))

    def lookup(self, uri=None, uris=None):
        if uris is not None:
            return dict((uri, self.lookup_one(uri)) for uri in uris)
        if uri is not None:
            return self.lookup_one(uri)
        return None

    def refresh(self, uri):
        pass

    def search_uri(self, query):
        type = uri.get_type(lookup_uri)
        if type == uri.ARTIST:
            artist = self.lookup_artist(uri.get_artist_id(lookup_uri))
            if artist is not None:
                return SearchResult(artists=[artist])
        elif type == uri.ALBUM:
            album = self.lookup_album(uri.get_album_id(lookup_uri))
            if album is not None:
                return SearchResult(albums=[album])
        elif type == uri.SONG:
            song = self.lookup_song(uri.get_song_id(lookup_uri))
            if song is not None:
                return SearchResult(tracks=[song])
        return None

    def search_by_artist_album_and_track(self, artist_name, album_name, track_name):
        tracks = self.search_by_artist_and_album(artist_name, album_name)
        track = next(item for item in tracks.tracks if track_name in item.name)
        return SearchResult(tracks=[track])

    def search_by_artist_and_album(self, artist_name, album_name):
        artists = self.subsonic_api.get_raw_artists()
        artist = next(item for item in artists if artist_name in item.get('name'))
        albums = self.subsonic_api.get_raw_albums(artist.get('id'))
        album = next(item for item in albums if album_name in item.get('title'))
        return SearchResult(tracks=self.subsonic_api.get_songs_as_tracks(album.get('id')))

    def get_distinct(self, field, query):
        search_result = self.search(query)
        if not search_result:
            return []
        if field == 'track' or field == 'title':
            return [track.name for track in (search_result.tracks or [])]
        if field == 'album':
            return [album.name for album in (search_result.albums or [])]
        if field == 'artist':
            if not search_result.artists:
                return [artist.name for artist in self.browse_artists()]
            return [artist.name for artist in search_result.artists]

    def search(self, query=None, uris=None, exact=False):
        if 'artist' in query and 'album' in query and 'track_name' in query:
            return self.search_by_artist_album_and_track(query.get('artist')[0], query.get('album')[0], query.get('track_name')[0])
        if 'artist' in query and 'album' in query:
            return self.search_by_artist_and_album(query.get('artist')[0], query.get('album')[0])
        if 'artist' in query:
            return self.subsonic_api.find_as_search_result(query.get('artist')[0])
        if 'any' in query:
            return self.subsonic_api.find_as_search_result(query.get('any')[0])
        return SearchResult(artists=self.subsonic_api.get_artists_as_artists())

