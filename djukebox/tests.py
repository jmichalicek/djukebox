from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TPE2

from models import *

import shutil
import os

# TODO: For many test cases there needs to be either some audio files included or something which will generate a dummy audio files.

# Due to fk to user, create these objects when needed in code
def create_artist(user, name='Test'):
    artist, created = Artist.objects.get_or_create(user=user, name=name)
    return artist

def create_album(user, artist, title='Test Album'):
    album, created = Album.objects.get_or_create(user=user, artist=artist, title=title)
    return album

# Using pre-created silent files for now.
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
        
class AlbumListViewTests(TestCase):
    """Test cases for views.album_list"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def test_logged_in(self):
        """Access the album_list view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('djukebox-albumlist'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the album_list view when not logged in"""
        response = self.client.get(reverse('djukebox-albumlist'))
        self.assertRedirects(response, '%s?next=%s' %(settings.LOGIN_URL, reverse('djukebox-albumlist')))

class AlbumViewTests(TestCase):
    """Test cases for views.album_songs"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')
        self.artist = create_artist(self.user)
        self.album = create_album(self.user, self.artist)

    def test_not_logged_in(self):
        """Access the album view while not logged in"""
        album = Album.objects.latest('id')
        response = self.client.get(reverse('djukebox-album', args=[album.id]))
        self.assertRedirects(response, '%s?next=%s' %(settings.LOGIN_URL, reverse('djukebox-album', args=[album.id])))

    def test_logged_in(self):
        album = Album.objects.latest('id')
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('djukebox-album', args=[album.id]))
        self.assertEqual(response.status_code, 200)
        context = response.context
        calbum = context['album']
        self.assertEqual(album.id, calbum.id)

class ArtistListViewTests(TestCase):
    """Test cases for views.artist_list"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def test_logged_in(self):
        """Access the artist_list view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('djukebox-artistlist'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the main view when not logged in"""
        response = self.client.get(reverse('djukebox-artistlist'))
        self.assertRedirects(response, '%s?next=%s' %(settings.LOGIN_URL, reverse('djukebox-artistlist')))

class TrackListViewTests(TestCase):
    """Test cases for views.track_list"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def test_logged_in(self):
        """Access the track_list view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('djukebox-tracklist'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the track_list view when not logged in"""
        response = self.client.get(reverse('djukebox-tracklist'))
        self.assertRedirects(response, '%s?next=%s' %(settings.LOGIN_URL, reverse('djukebox-tracklist')))

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
