from mopidy import backend
from mopidy_subidy import uri
from mopidy.models import Playlist

import logging
logger = logging.getLogger(__name__)

class SubidyPlaylistsProvider(backend.PlaylistsProvider):
    def __init__(self, *args, **kwargs):
        super(SubidyPlaylistsProvider, self).__init__(*args, **kwargs)
        self.subsonic_api = self.backend.subsonic_api
        self.playlists = []
        self.refresh()

    def as_list(self):
        return self.subsonic_api.get_playlists_as_refs()

    def create(self, name):
        result = self.subsonic_api.create_playlist_raw(name)
        if result is None:
            return None
        playlist = result.get('playlist')
        if playlist is None:
            for pl in self.subsonic_api.get_playlists_as_playlists():
                if pl.name == name:
                    playlist = pl
            return playlist
        else:
            return self.subsonic_api.raw_playlist_to_playlist(playlist)

    def delete(self, playlist_uri):
        playlist_id = uri.get_playlist_id(playlist_uri)
        self.subsonic_api.delete_playlist_raw(playlist_id)

    def get_items(self, items_uri):
        #logger.info('ITEMS %s: %s' % (lookup_uri, self.subsonic_api.get_playlist_songs_as_refs(uri.get_playlist_id(items_uri))))
        return self.subsonic_api.get_playlist_as_songs_as_refs(uri.get_playlist_id(items_uri))

    def lookup(self, lookup_uri):
        #logger.info('LOOKUP PLAYLIST %s: %s' % (lookup_uri, self.subsonic_api.get_playlist_as_playlist(uri.get_playlist_id(lookup_uri))))
        return self.subsonic_api.get_playlist_as_playlist(uri.get_playlist_id(lookup_uri))

    def refresh(self):
        pass

    def save(self, playlist):
        playlist_id = uri.get_playlist_id(playlist.uri)
        track_ids = []
        for trk in playlist.tracks:
            track_ids.append(uri.get_song_id(trk.uri))
        result = self.subsonic_api.save_playlist_raw(playlist_id, track_ids)
        if result is None:
            return None
        return playlist
