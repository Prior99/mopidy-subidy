from urlparse import urlparse
import libsonic
import logging
import itertools
from mopidy.models import Track, Album, Artist, Playlist, Ref
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

    def find_artists_by_name(self, artist_name):
        response = self.connection.search3(artist_name, MAX_SEARCH_RESULTS, 0, 0, 0, 0, 0)
        if response.get('status') != RESPONSE_OK:
            return None
        artists = response.get('searchResult3').get('artist')
        if artists is not None:
            return [self.raw_artist_to_artist(artist) for artist in artists]
        return None

    def find_tracks_by_name(self, track_name):
        response = self.connection.search3(track_name, 0, 0, 0, 0, MAX_SEARCH_RESULTS, 0)
        if response.get('status') != RESPONSE_OK:
            return None
        tracks = response.get('searchResult3').get('song')
        if tracks is not None:
            return [self.raw_song_to_track(track) for track in tracks]
        return None

    def find_albums_by_name(self, album_name):
        response = self.connection.search3(album_name, 0, 0, MAX_SEARCH_RESULTS, 0, 0, 0)
        if response.get('status') != RESPONSE_OK:
            return None
        albums = response.get('searchResult3').get('album')
        if albums is not None:
            return [self.raw_album_to_album(album) for album in albums]
        return None

    def get_raw_artists(self):
        response = self.connection.getIndexes()
        if response.get('status') != RESPONSE_OK:
            return None
        letters = response.get('indexes').get('index')
        if letters is not None:
            return [artist for letter in letters for artist in letter.get('artist')]
        return None

    def find_song_by_id(self, song_id):
        response = self.connection.getSong(song_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return self.raw_song_to_track(response.get('song')) if response.get('song') is not None else None

    def find_album_by_id(self, album_id):
        response = self.connection.getAlbum(album_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return self.raw_album_to_album(response.get('album')) if response.get('album') is not None else None

    def find_artist_by_id(self, artist_id):
        response = self.connection.getArtist(artist_id)
        if response.get('status') != RESPONSE_OK:
            return None
        return self.raw_artist_to_artist(response.get('artist')) if response.get('artist') is not None else None

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
        return sorted([self.raw_album_to_ref(album) for album in self.get_raw_albums(artist_id)], key=ref_sort_key)

    def get_albums_as_albums(self, artist_id):
        return sorted([self.raw_album_to_album(album) for album in self.get_raw_albums(artist_id)], key=ref_sort_key)

    def get_songs_as_refs(self, album_id):
        return sorted([self.raw_song_to_ref(song) for song in self.get_raw_songs(album_id)], key=ref_sort_key)

    def get_songs_as_tracks(self, album_id):
        return sorted([self.raw_song_to_track(song) for song in self.get_raw_songs(album_id)], key=ref_sort_key)

    def get_artists_as_refs(self):
        return sorted([self.raw_artist_to_ref(artist) for artist in self.get_raw_artists()], key=ref_sort_key)

    def get_artists_as_artists(self):
        return sorted([self.raw_artist_to_artist(artist) for artist in self.get_raw_artists()], key=lambda artist:artist.name)

    def raw_song_to_ref(self, song):
        return Ref(
            name=song.get('title') or UNKNOWN_SONG,
            uri=uri.get_song_uri(song.get('id')),
            type=Ref.TRACK)

    def raw_song_to_track(self, song):
        album_name = song.get('album')
        album = self.find_albums_by_name(album_name)[0] if album_name is not None else None
        artist_name = song.get('artist')
        artist = self.find_artists_by_name(artist_name)[0] if artist_name is not None else None
        return Track(
            name=song.get('title') or UNKNOWN_SONG,
            uri=uri.get_song_uri(song.get('id')),
            bitrate=song.get('bitRate'),
            track_no=int(song.get('track')) if song.get('track') else None,
            date=str(song.get('year')) or 'none',
            genre=song.get('genre'),
            length=int(song.get('duration')) * 1000 if song.get('duration') else None,
            disc_no=int(song.get('discNumber')) if song.get('discNumber') else None,
            artists=[artist] if artist is not None else None,
            album=album
        )
    def raw_album_to_ref(self, album):
        return Ref(
            name=album.get('title') or album.get('name') or UNKNOWN_ALBUM,
            uri=uri.get_album_uri(album.get('id')),
            type=Ref.ALBUM)

    def raw_album_to_album(self, album):
        artist_name = album.get('artist')
        artist = self.find_artists_by_name(artist_name)[0] if artist_name is not None else None
        return Album(
            name=album.get('title') or album.get('name') or UNKNOWN_ALBUM,
            uri=uri.get_album_uri(album.get('id')),
            artists=[artist]
        )

    def raw_artist_to_ref(self, artist):
        return Ref(
            name=artist.get('name') or UNKNOWN_ARTIST,
            uri=uri.get_artist_uri(artist.get('id')),
            type=Ref.ARTIST)

    def raw_artist_to_artist(self, artist):
        return Artist(
            name=artist.get('name') or UNKNOWN_ARTIST,
            uri=uri.get_artist_uri(artist.get('id'))
        )
