import mopidy_subidy
from mopidy_subidy import library, playback, playlists, subsonic_api
from mopidy import backend
import pykka

class SubidyBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(SubidyBackend, self).__init__()
        subidy_config = config['subidy']
        self.subsonic_api = subsonic_api.SubsonicApi(
            url=subidy_config['url'],
            username=subidy_config['username'],
            password=subidy_config['password'],
            app_name=mopidy_subidy.SubidyExtension.dist_name,
            legacy_auth=subidy_config['legacy_auth'],
            api_version=subidy_config['api_version'])
        self.library = library.SubidyLibraryProvider(backend=self)
        self.playback = playback.SubidyPlaybackProvider(audio=audio, backend=self)
        self.playlists = playlists.SubidyPlaylistsProvider(backend=self)
        self.uri_schemes = ['subidy']
