from mopidy import backend, models
from mopidy_subidy import uri

class SubidyLibraryProvider(backend.LibraryProvider):
    root_directory = models.Ref(uri=uri.ROOT_URI, type=models.Ref.DIRECTORY, name='Subsonic')

    def __init__(self, *args, **kwargs):
        super(SubidyLibraryProvider, self).__init__(*args, **kwargs)
        self.subsonic_api = self.backend.subsonic_api

    def browse_songs(self,album_id):
        return self.subsonic_api.get_songs_as_refs(album_id)

    def browse_albums(self, artist_id):
        return self.subsonic_api.get_albums_as_refs(artist_id)

    def browse_artists(self):
        return self.subsonic_api.get_artists_as_refs()

    def lookup_song(self, song_id):
        return self.subsonic_api.find_song_by_id(song_id)

    def lookup_album(self, album_id):
        return self.subsonic_api.find_album_by_id(album_id)

    def lookup_artist(self, artist_id):
        return self.subsonic_api.find_artist_by_id(artist_id)

    def browse(self, browse_uri):
        type = uri.get_type(browse_uri)
        if browse_uri == uri.ROOT_URI:
            return self.browse_artists()
        if type == uri.ARTIST:
            return self.browse_albums(uri.get_artist_id(browse_uri))
        if type == uri.ALBUM:
            return self.browse_songs(uri.get_album_id(browse_uri))
    
    def lookup_one(self, lookup_uri):
        type = uri.get_type(lookup_uri)
        if type == uri.ARTIST:
            return self.lookup_artist(uri.get_artist_id(lookup_uri))
        if type == uri.ALBUM:
            return self.lookup_album(uri.get_album_id(lookup_uri))
        if type == uri.SONG:
            return self.lookup_song(uri.get_song_id(lookup_uri))

    def lookup(self, uri=None, uris=None):
        if uris is not None:
            return [self.lookup_one(uri) for uri in uris]
        if uri is not None:
            return [self.lookup_one(uri)]
        return None

    def refresh(self, uri):
        pass
    def search(self, query=None, uris=None, exact=False):
        pass
