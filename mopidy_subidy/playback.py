import logging

from mopidy import backend
from mopidy_subidy import uri

logger = logging.getLogger(__name__)


class SubidyPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subsonic_api = self.backend.subsonic_api

    def translate_uri(self, translate_uri):
        song_id = uri.get_song_id(translate_uri)
        censored_url = self.subsonic_api.get_censored_song_stream_uri(song_id)
        logger.debug("Loading song from subsonic with url: '%s'" % censored_url)
        return self.subsonic_api.get_song_stream_uri(song_id)
