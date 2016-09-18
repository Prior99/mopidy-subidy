from mopidy import backend

class SubidyPlaylistsProvider(backend.PlaylistsProvider):
    def __init__(self, *args, **kwargs):
        super(SubidyPlaylistsProvider, self).__init__(*args, **kwargs)
        self.playlists = []

    def as_list(self):
        pass

    def create(self, name):
        pass

    def delete(self, uri):
        pass

    def get_items(self, uri):
        pass

    def lookup(self, uri):
        pass

    def refresh(self):
        pass

    def save(self, playlist):
        pass
