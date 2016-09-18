from urlparse import urlparse
import libsonic
import logging
import itertools
from mopidy.models import Track, Album, Artist, Playlist, Ref, SearchResult
from mopidy_subidy import uri

logger = logging.getLogger(__name__)

RESPONSE_OK = u'ok'
UNKNOWN_SONG = u'Unknown Song'
UNKNOWN_ALBUM = u'Unknown Album'
UNKNOWN_ARTIST = u'Unknown Artist'
MAX_SEARCH_RESULTS = 100

ref_sort_key = lambda ref: ref.name

class SubsonicApi():
    def __init__(self, url, username, password):
        parsed = urlparse(url)
        self.port = parsed.port if parsed.port else \
            443 if parsed.scheme == 'https' else 80
        base_url = parsed.scheme + '://' + parsed.hostname
        self.connection = libsonic.Connection(
            base_url,
            username,
            password,
            self.port,
            parsed.path + '/rest')
        self.url = url + '/rest'
        self.username = username
        self.password = password
        logger.info('Connecting to subsonic server on url %s as user %s' % (url, username))
        try:
            self.connection.ping()
        except Exception as e:
            logger.error('Unabled to reach subsonic server: %s' % e)
            exit()

    def get_song_stream_uri(self, song_id):
        template = '%s/stream.view?id=%s&u=%s&p=%s&c=mopidy&v=1.14'
        return template % (self.url, song_id, self.username, self.password)

    def find_raw(self, query, exclude_artists=False, exclude_albums=False, exclude_songs=False):
        response = self.connection.search2(
            query.encode('utf-8'),
            MAX_SEARCH_RESULTS if not exclude_artists else 0, 0,
            MAX_SEARCH_RESULTS if not exclude_albums else 0, 0,
            MAX_SEARCH_RESULTS if not exclude_songs else 0, 0)
        if response.get('status') != RESPONSE_OK:
            return None
        return response.get('searchResult2')

    def find_as_search_result(self, query, exclude_artists=False, exclude_albums=False, exclude_songs=False):
        result = self.find_raw(query)
        return SearchResult(
            uri=uri.get_search_uri(query),
            artists=[self.raw_artist_to_artist(artist) for artist in result.get('artist') or []],
            albums=[self.raw_album_to_album(album) for album in result.get('album') or []],
            tracks=[self.raw_song_to_track(song) for song in result.get('song') or []])


    def get_raw_artists(self):
        response = self.connection.getIndexes()
        if response.get('status') != RESPONSE_OK:
            return None
        letters = response.get('indexes').get('index')
        if letters is not None:
            artists = [artist for letter in letters for artist in letter.get('artist')]
            return artists
        return None

    def get_song_by_id(self, song_id):
        response = self.connection.getSong(song_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return self.raw_song_to_track(response.get('song')) if response.get('song') is not None else None

    def get_album_by_id(self, album_id):
        response = self.connection.getAlbum(album_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return self.raw_album_to_album(response.get('album')) if response.get('album') is not None else None

    def get_artist_by_id(self, artist_id):
        response = self.connection.getArtist(artist_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return self.raw_artist_to_artist(response.get('artist')) if response.get('artist') is not None else None

    def get_raw_playlists(self):
        response = self.connection.getPlaylists()
        if response.get('status') != RESPONSE_OK:
            return None
        return response.get('playlists').get('playlist')

    def get_raw_playlist(self, playlist_id):
        response = self.connection.getPlaylist(playlist_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return response.get('playlist')

    def get_raw_dir(self, parent_id):
        response = self.connection.getMusicDirectory(parent_id)
        if response.get('status') != RESPONSE_OK:
            return None
        directory = response.get('directory')
        if directory is not None:
            return directory.get('child')
        return None

    def get_raw_albums(self, artist_id):
        return self.get_raw_dir(artist_id)

    def get_raw_songs(self, album_id):
        return self.get_raw_dir(album_id)

    def get_albums_as_refs(self, artist_id):
        return [self.raw_album_to_ref(album) for album in self.get_raw_albums(artist_id)]

    def get_albums_as_albums(self, artist_id):
        return [self.raw_album_to_album(album) for album in self.get_raw_albums(artist_id)]

    def get_songs_as_refs(self, album_id):
        return [self.raw_song_to_ref(song) for song in self.get_raw_songs(album_id)]

    def get_songs_as_tracks(self, album_id):
        return [self.raw_song_to_track(song) for song in self.get_raw_songs(album_id)]

    def get_artists_as_refs(self):
        return [self.raw_artist_to_ref(artist) for artist in self.get_raw_artists()]

    def get_artists_as_artists(self):
        return [self.raw_artist_to_artist(artist) for artist in self.get_raw_artists()]

    def get_playlists_as_refs(self):
        return [self.raw_playlist_to_ref(playlist) for playlist in self.get_raw_playlists()]

    def get_playlists_as_playlists(self):
        return [self.raw_playlist_to_playlist(playlist) for playlist in self.get_raw_playlists()]

    def get_playlist_as_playlist(self, playlist_id):
        return self.raw_playlist_to_playlist(self.get_raw_playlist(playlist_id))

    def get_playlist_as_songs_as_refs(self, playlist_id):
        playlist = self.get_raw_playlist(playlist_id)
        return [self.raw_song_to_ref(song) for song in playlist.get('entry')]

    def raw_song_to_ref(self, song):
        return Ref.track(
            name=song.get('title') or UNKNOWN_SONG,
            uri=uri.get_song_uri(song.get('id')))

    def raw_song_to_track(self, song):
        return Track(
            name=song.get('title') or UNKNOWN_SONG,
            uri=uri.get_song_uri(song.get('id')),
            bitrate=song.get('bitRate'),
            track_no=int(song.get('track')) if song.get('track') else None,
            date=str(song.get('year')) or 'none',
            genre=song.get('genre'),
            length=int(song.get('duration')) * 1000 if song.get('duration') else None,
            disc_no=int(song.get('discNumber')) if song.get('discNumber') else None,
            artists=[Artist(
                name=song.get('artist'),
                uri=uri.get_artist_uri(song.get('artistId')))],
            album=Album(
                name=song.get('album'),
                uri=uri.get_album_uri('albumId')))
    def raw_album_to_ref(self, album):
        return Ref.album(
            name=album.get('title') or album.get('name') or UNKNOWN_ALBUM,
            uri=uri.get_album_uri(album.get('id')))

    def raw_album_to_album(self, album):
        return Album(
            name=album.get('title') or album.get('name') or UNKNOWN_ALBUM,
            uri=uri.get_album_uri(album.get('id')),
            artists=[Artist(
                name=album.get('artist'),
                uri=uri.get_artist_uri(album.get('artistId')))])

    def raw_artist_to_ref(self, artist):
        return Ref.artist(
            name=artist.get('name') or UNKNOWN_ARTIST,
            uri=uri.get_artist_uri(artist.get('id')))

    def raw_artist_to_artist(self, artist):
        return Artist(
            name=artist.get('name') or UNKNOWN_ARTIST,
            uri=uri.get_artist_uri(artist.get('id')))

    def raw_playlist_to_playlist(self, playlist):
        entries = playlist.get('entry')
        tracks = [self.raw_song_to_track(song) for song in entries] if entries is not None else None
        return Playlist(
            uri=uri.get_playlist_uri(playlist.get('id')),
            name=playlist.get('name'),
            tracks=tracks)

    def raw_playlist_to_ref(self, playlist):
        return Ref.playlist(
            uri=uri.get_playlist_uri(playlist.get('id')),
            name=playlist.get('name'))
