from mopidy import backend
from mopidy_subidy import uri

import logging
logger = logging.getLogger(__name__)

class SubidyPlaylistsProvider(backend.PlaylistsProvider):
    def __init__(self, *args, **kwargs):
        super(SubidyPlaylistsProvider, self).__init__(*args, **kwargs)
        self.subsonic_api = self.backend.subsonic_api
        self.playlists = []
        self.refresh()

    def as_list(self):
        return self.playlists

    def create(self, name):
        pass

    def delete(self, uri):
        pass

    def get_items(self, items_uri):
        #logger.info('ITEMS %s: %s' % (lookup_uri, self.subsonic_api.get_playlist_songs_as_refs(uri.get_playlist_id(items_uri))))
        return self.subsonic_api.get_playlist_as_songs_as_refs(uri.get_playlist_id(items_uri))

    def lookup(self, lookup_uri):
        #logger.info('LOOKUP PLAYLIST %s: %s' % (lookup_uri, self.subsonic_api.get_playlist_as_playlist(uri.get_playlist_id(lookup_uri))))
        return self.subsonic_api.get_playlist_as_playlist(uri.get_playlist_id(lookup_uri))

    def refresh(self):
        self.playlists = self.subsonic_api.get_playlists_as_refs()

    def save(self, playlist):
        pass
