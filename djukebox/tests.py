"""
WARNING!  Several of these tests currently ASSUME a test system and could result in a loss of data.
That is unlikely as the files are all put in directories suggesting they were created in the past,
but I cannot control what else you do, so it IS possible.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import client

from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TPE2

from models import *

import json
import shutil
import os
import types

# TODO: For many test cases there needs to be either some audio files included or something which will generate a dummy audio files.

# Due to fk to user, create these objects when needed in code
def create_artist(user, name='Test'):
    artist, created = Artist.objects.get_or_create(user=user, name=name)
    return artist

def create_album(user, artist, title='Test Album'):
    album, created = Album.objects.get_or_create(user=user, artist=artist, title=title)
    return album

# Using pre-created silent files for now.
# These could be used to create silent files on the fly
#def ffmpeg_create_empty_mp3():
#    """Create a 1 second silent mp3 using ffmpeg"""
#    ffmpeg -ar 44100 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -t 00:00:01 test.mp3

#def ffmpeg_create_empty_ogg():
#    """Create a 1 second silent oga using ffmpeg"""
#    ffmpeg -ar 44100 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -t 00:00:01 -acodec libvorbis test.ogg

#def sox_create_empty_mp3():
#    """Create a 1 second silent mp3 using sox"""
#    sox -n silent.mp3 trim 0 1

#def sox_create_empty_ogg():
#    """Create a 1 second silent ogg using sox"""
#    sox -n -t ogg silent.ogg trim 0 1


class MainViewTests(TestCase):
    """Test cases for views.home"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def test_logged_in(self):
        """Access the main view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('djukebox-home'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the main view when not logged in"""
        response = self.client.get(reverse('djukebox-home'))
        self.assertRedirects(response, '%s?next=%s' %(settings.LOGIN_URL, reverse('djukebox-home')))


class AudioFileTests(TestCase):
    """Test the AudioFile class"""
    fixtures = ['test_audiofilemodeltests']

    def setUp(self):
        self.audiofile = AudioFile.objects.get(id=1)

        dest_file = os.path.join(settings.MEDIA_ROOT,
                                self.audiofile.file.name)

        #if not os.path.exists(os.path.join(dest_file, 'silent.ogg')):
            #current_dir = os.path.dirname(os.path.abspath(__file__))
            #source_ogg = os.path.join(current_dir, 'test_audio/silent.ogg')
            #shutil.copyfile(source_ogg, dest_file)


class AudioFileUnicodeTests(AudioFileTests):
    """Test the __unicode__() method of the AudioFile class"""

    def test__unicode(self):
        self.assertEqual(self.audiofile.file.name, self.audiofile.__unicode__())


class OggFileTests(TestCase):
    """Test the OggFile class"""
    fixtures = ['test_oggfilemodeltests']

    # I can't get manage to straight monkey patch or use mock.patch
    # to properly mock out mutagen.oggvorbis.OggVorbis, so just use
    # small dummy audio files and the full classes for now.  This is
    # what the actual mutagen test cases do.
    # Most of the test cases actually still patch the .get() method and the
    # value it returns, but the file needs to exist for the OggVorbis object
    # to be instantiated.
    def setUp(self):
        self.oggfile = OggFile.objects.get(id=1)

        self.dest_file = os.path.join(settings.MEDIA_ROOT,
                                      self.oggfile.file.name)
        self.dest_dir = os.path.dirname(self.dest_file)

        if not os.path.exists(self.dest_dir):
            os.makedirs(self.dest_dir)

        if os.path.exists(self.dest_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            source_ogg = os.path.join(current_dir, 'test_audio/silent.ogg')
            shutil.copyfile(source_ogg, self.dest_file)

    def tearDown(self):
        # CAREFUL!  This could actually delete a real file.
        if os.path.exists(self.dest_file):
            os.remove(self.dest_file)

        # Don't delete the dir if there are other files in there
        if os.path.exists(self.dest_dir) and not os.listdir(self.dest_dir):
            # Will blow up if this is a sym link...
            # make that be the case and find a better way to do it
            shutil.rmtree(self.dest_dir)


class OggFileUnicodeTests(OggFileTests):
    """Test the __unicode__() method of the OggFile class"""

    def test__unicode(self):
        self.assertEqual(self.oggfile.file.name, self.oggfile.__unicode__())


class OggFileGetTitleTests(OggFileTests):
    """Test the get_title() method of the OggFile class"""

    def test_get_title(self):
        def fake_get(a, b, c):
            return ['Fake Title']

        orig = OggVorbis.get
        OggVorbis.get = fake_get
        self.assertEqual('Fake Title', self.oggfile.get_title())
        OggVorbis.get = orig


class OggFileGetArtistTests(OggFileTests):
    """Test the get_artist() method of the OggFile class"""

    def test_get_artist(self):
        def fake_get(a,b,c):
            return ['Fake Artist']

        orig = OggVorbis.get
        OggVorbis.get = fake_get
        self.assertEqual('Fake Artist', self.oggfile.get_artist())
        OggVorbis.get = orig


class OggFileGetAlbumTests(OggFileTests):
    """Test the get_album() method of the OggFile class"""

    def test_get_album(self):
        def fake_get(a,b,c):
            return ['Fake Album']

        orig = OggVorbis.get
        OggVorbis.get = fake_get
        self.assertEqual('Fake Album', self.oggfile.get_album())
        OggVorbis.get = orig


class Mp3FileTests(TestCase):
    """Test the Mp3File class"""
    fixtures = ['test_mp3filemodeltests']

    # I can't get manage to straight monkey patch or use mock.patch
    # to properly mock out mutagen.easyid3.EasyID3, so just use
    # small dummy audio files and the full classes for now.  This is
    # what the actual mutagen test cases do.

    def setUp(self):
        self.mp3file = Mp3File.objects.get(id=1)

        self.dest_file = os.path.join(settings.MEDIA_ROOT,
                                 self.mp3file.file.name)

        self.dest_dir = os.path.dirname(self.dest_file)
        if not os.path.exists(self.dest_dir):
            os.makedirs(self.dest_dir)

        if not os.path.exists(self.dest_file):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            source_mp3 = os.path.join(current_dir, 'test_audio/silent.mp3')
            shutil.copyfile(source_mp3, self.dest_file)

    def tearDown(self):
        dest_file = os.path.join(settings.MEDIA_ROOT,
                                 self.mp3file.file.name)

        if os.path.exists(self.dest_file):
            os.remove(self.dest_file)

        # Don't delete the dir if there are other files in there
        if os.path.exists(self.dest_dir) and not os.listdir(self.dest_dir):
            # Will blow up if this is a sym link...
            # make that be the case and find a better way to do it
            shutil.rmtree(self.dest_dir)


class Mp3FileUnicodeTests(Mp3FileTests):
    """Test the __unicode__() method of the Mp3File class"""

    def test__unicode(self):
        self.assertEqual(self.mp3file.file.name, self.mp3file.__unicode__())


class Mp3FileGetTitleTests(Mp3FileTests):
    """Test the get_title() method of the OggFile class"""

    def test_single_title(self):
        def fake_get(a,b,c):
            return ['Fake Title']

        orig = EasyID3.get
        EasyID3.get = fake_get
        self.assertEqual('Fake Title', self.mp3file.get_title())
        EasyID3.get = orig


class Mp3SourceConversionTests(TestCase):
    fixtures = ['test_mp3filemodeltests']

    def setUp(self):
        self.mp3file = Mp3File.objects.get(id=1)

        dest_file = os.path.join(settings.MEDIA_ROOT,
                                 self.mp3file.file.name)

        if not os.path.exists(dest_file):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            source_mp3 = os.path.join(current_dir, 'test_audio/silent.mp3')
            shutil.copyfile(source_mp3, dest_file)

    def tearDown(self):
        dest_file = os.path.join(settings.MEDIA_ROOT,
                                 self.mp3file.file.name)

        if os.path.exists(dest_file):
            os.remove(dest_file)


class OggSourceConversionTests(TestCase):
    fixtures = ['test_oggfilemodeltests']

    def setUp(self):
        self.oggfile = OggFile.objects.get(id=1)

        dest_file = os.path.join(settings.MEDIA_ROOT,
                                 self.oggfile.file.name)

        if not os.path.exists(dest_file):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            source_ogg = os.path.join(current_dir, 'test_audio/silent.ogg')
            shutil.copyfile(source_ogg, dest_file)

    def tearDown(self):
        dest_file = os.path.join(settings.MEDIA_ROOT,
                                 self.oggfile.file.name)
        if os.path.exists(dest_file):
            os.remove(dest_file)


class FileConversionUnitTests(TestCase):
    def test_convert_file_to_ogg_task(self):
        pass

    def test_convert_file_to_mp3_task(self):
        pass

    def test_DjukeboxMp3FromOgg(self):
        pass

    def test_DjukeboxOggFromMp3(self):
        pass


# Master branch has handy ResourceTestCase
class ApiTests(TestCase):
    """Test the REST API"""

    fixtures = ['djukebox_api_tests']

    def setUp(self):
        super(ApiTests, self).setUp()
        self.user = User.objects.get(id=1)
        self.user.set_password('test')
        self.user.save()

    def tearDown(self):
        super(ApiTests, self).tearDown()
        self.client.logout()


class AlbumResourceTests(ApiTests):
    """Test usage of the AlbumResource"""

    def test_get_list_not_logged_in(self):
        self.client.logout()
        request_args = {'resource_name': 'album',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args))

        self.assertEqual(response.status_code, 401)


    def test_get_list(self):
        """Test the default behavior getting the AlbumResource list"""

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'album',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('albums' in returned)
        self.assertEqual(len(returned['albums']), 2)
        first = returned['albums'][0]
        self.assertEqual(type(first['artist']), types.UnicodeType)
        self.assertEqual(type(first['tracks'][0]), types.UnicodeType)

    def test_get_list_artist_details(self):
        """Test getting the AlbumResource list with Artist details"""

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'album',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args), data={'details': 'artist'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('albums' in returned)
        self.assertEqual(len(returned['albums']), 2)
        first = returned['albums'][0]
        self.assertEqual(type(first['artist']), types.DictType)
        self.assertTrue('name' in first['artist'])

    def test_get_list_track_details(self):
        """Test getting the AlbumResource list with Track details"""

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'album',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args), data={'details': 'track'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('albums' in returned)
        self.assertEqual(len(returned['albums']), 2)
        first = returned['albums'][0]
        self.assertEqual(type(first['tracks'][0]), types.DictType)
        self.assertTrue('title' in first['tracks'][0])

    def test_get_details(self):
        """Test the default behavior getting the AlbumResource details"""

        album = Album.objects.all()[0]

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'album',
                        'api_name': 'v1',
                        'pk': album.pk}

        response = self.client.get(reverse(
                'api_dispatch_detail',
                kwargs=request_args))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('tracks' in returned)
        self.assertTrue('title' in returned)
        self.assertTrue('artist' in returned)
        self.assertEqual(type(returned['artist']), types.UnicodeType)
        self.assertEqual(type(returned['tracks'][0]), types.UnicodeType)

    def test_get_details_artist_details(self):
        """Test the default behavior getting the AlbumResource details"""

        album = Album.objects.all()[0]

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'album',
                        'api_name': 'v1',
                        'pk': album.pk}

        response = self.client.get(reverse(
                'api_dispatch_detail',
                kwargs=request_args), data={'details': 'artist'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('tracks' in returned)
        self.assertTrue('title' in returned)
        self.assertTrue('artist' in returned)
        self.assertEqual(type(returned['artist']), types.DictType)
        self.assertEqual(type(returned['tracks'][0]), types.UnicodeType)

    def test_get_details_track_details(self):
        """Test the default behavior getting the AlbumResource details"""

        album = Album.objects.all()[0]

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'album',
                        'api_name': 'v1',
                        'pk': album.pk}

        response = self.client.get(reverse(
                'api_dispatch_detail',
                kwargs=request_args), data={'details': 'track'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('tracks' in returned)
        self.assertTrue('title' in returned)
        self.assertTrue('artist' in returned)
        self.assertEqual(type(returned['artist']), types.UnicodeType)
        self.assertEqual(type(returned['tracks'][0]), types.DictType)

class ArtistResourceTests(ApiTests):
    """Test usage of the ArtistResource"""

    def test_get_list_not_logged_in(self):
        self.client.logout()
        request_args = {'resource_name': 'artist',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args))

        self.assertEqual(response.status_code, 401)


    def test_get_list(self):
        """Test the default behavior getting the AlbumResource list"""
        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'artist',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('artists' in returned)
        self.assertEqual(len(returned['artists']), 2)
        first = returned['artists'][0]
        self.assertEqual(type(first['name']), types.UnicodeType)

    def test_get_artist_details(self):
        """Test the default behavior getting the ArtistResource details"""
        self.client.login(username=self.user.username,
                          password='test')

        artist = Artist.objects.all()[0]

        request_args = {'resource_name': 'artist',
                        'api_name': 'v1',
                        'pk': artist.pk}

        response = self.client.get(reverse(
                'api_dispatch_detail',
                kwargs=request_args))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('name' in returned)
        self.assertEqual(returned['name'], artist.name)
        self.assertEqual(int(returned['id']), artist.id)

class TrackResourceTests(ApiTests):
    """Test usage of the TrackResource"""

    def test_get_list_not_logged_in(self):
        self.client.logout()
        request_args = {'resource_name': 'track',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args))

        self.assertEqual(response.status_code, 401)

    def test_get_list(self):
        """Test the default behavior getting the TrackResource list"""

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'track',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)

        self.assertTrue('tracks' in returned)
        self.assertEqual(len(returned['tracks']), 3)
        first = returned['tracks'][0]
        self.assertEqual(type(first['album']), types.UnicodeType)
        self.assertEqual(type(first['title'][0]), types.UnicodeType)
        self.assertEqual(type(first['ogg_stream_url']), types.UnicodeType)
        self.assertEqual(type(first['mp3_stream_url']), types.UnicodeType)

    def test_get_list_album_details(self):
        """Test TrackResource list with album details"""

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'track',
                        'api_name': 'v1'}

        response = self.client.get(reverse(
                'api_dispatch_list',
                kwargs=request_args), data={'details': 'album'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)

        self.assertTrue('tracks' in returned)
        self.assertEqual(len(returned['tracks']), 3)
        first = returned['tracks'][0]
        self.assertEqual(type(first['album']), types.DictType)
        self.assertEqual(type(first['title'][0]), types.UnicodeType)
        self.assertEqual(type(first['ogg_stream_url']), types.UnicodeType)
        self.assertEqual(type(first['mp3_stream_url']), types.UnicodeType)

        check_track = Track.objects.get(id=int(first['id']))
        self.assertEqual(first['album']['title'], check_track.album.title)

    def test_get_details(self):
        """Test the default behavior getting the TrackResource details"""

        track = Track.objects.all()[0]

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'track',
                        'api_name': 'v1',
                        'pk': track.pk}

        response = self.client.get(reverse(
                'api_dispatch_detail',
                kwargs=request_args))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)

        self.assertTrue('mp3_stream_url' in returned)
        self.assertTrue('ogg_stream_url' in returned)
        self.assertTrue('album' in returned)
        self.assertTrue('title' in returned)
        self.assertTrue('track_number' in returned)
        self.assertTrue('id' in returned)
        self.assertEqual(type(returned['album']), types.UnicodeType)
        self.assertEqual(type(returned['title']), types.UnicodeType)
        self.assertEqual(type(returned['mp3_stream_url']), types.UnicodeType)
        self.assertEqual(type(returned['ogg_stream_url']), types.UnicodeType)

    def test_get_details_album_details(self):
        """Test getting the TrackResource details with album details"""

        track = Track.objects.all()[0]

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'track',
                        'api_name': 'v1',
                        'pk': track.pk}

        response = self.client.get(reverse(
                'api_dispatch_detail',
                kwargs=request_args), data={'details': 'album'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))

        returned = json.loads(response.content)
        self.assertTrue('mp3_stream_url' in returned)
        self.assertTrue('ogg_stream_url' in returned)
        self.assertTrue('album' in returned)
        self.assertTrue('title' in returned)
        self.assertTrue('track_number' in returned)
        self.assertTrue('id' in returned)
        self.assertEqual(type(returned['album']), types.DictType)
        self.assertEqual(type(returned['title']), types.UnicodeType)
        self.assertEqual(type(returned['mp3_stream_url']), types.UnicodeType)
        self.assertEqual(type(returned['ogg_stream_url']), types.UnicodeType)

    def test_delete_details(self):
        """Test deleting a track"""
        track = Track.objects.all()[0]

        self.client.login(username=self.user.username,
                          password='test')

        request_args = {'resource_name': 'track',
                        'api_name': 'v1',
                        'pk': track.pk}

        response = self.client.delete(reverse(
                'api_dispatch_detail',
                kwargs=request_args))

        self.assertEqual(response.status_code, 204)
        self.assertTrue(response['Content-Type'].startswith('text/html'))

    def test_delete_details_not_logged_in(self):
        """Test deleting a track"""
        track = Track.objects.all()[0]

        self.client.logout()

        request_args = {'resource_name': 'track',
                        'api_name': 'v1',
                        'pk': track.pk}

        response = self.client.delete(reverse(
                'api_dispatch_detail',
                kwargs=request_args))

        self.assertEqual(response.status_code, 401)
        self.assertTrue(response['Content-Type'].startswith('text/html'))

class TrackAlbumResourceTests(ApiTests):

    def setUp(self):
        super(TrackAlbumResourceTests, self).setUp()

    def test_update_track_title(self):
        artist = Artist.objects.create(name='Justin Michalicek', user=self.user)
        album = Album.objects.create(title='Justin Rocks Out', artist=artist, user=self.user)
        track = Track.objects.create(title='Justin Is Currently Rocking', album=album, artist=artist, user=self.user)

        new_data = {
            'track_artist': track.artist.name + ' 2',
            'track_title': track.title + ' 2',
            'album_artist': album.artist.name,
            'album_title': album.title
            }

        reverse_kwargs = {'resource_name': 'track_album', 'api_name': 'v1', 'pk': track.pk}
        # this should work after upgrade to django 1.6
        response = self.client.patch(reverse('api_dispatch_detail', kwargs=reverse_kwargs),
                                     new_data)

        self.assertEqual(response.status_code, 200)
