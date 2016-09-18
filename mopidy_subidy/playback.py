from mopidy import backend
from mopidy_subidy import uri

class SubidyPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, *args, **kwargs):
        super(SubidyPlaybackProvider, self).__init__(*args, **kwargs)
        self.subsonic_api = self.backend.subsonic_api

    def translate_uri(self, translate_uri):
        return self.subsonic_api.get_song_stream_uri(uri.get_song_id(translate_uri))
