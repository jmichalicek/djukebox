from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# TODO: For many test cases there needs to be either some audio files included or something which will generate a dummy audio files.

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
        """Access the album view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('djukebox-albumlist'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the album_list view when not logged in"""
        response = self.client.get(reverse('djukebox-albumlist'))
        self.assertRedirects(response, '%s?next=%s' %(settings.LOGIN_URL, reverse('djukebox-albumlist')))

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

class OggFileUnitTests(TestCase):
    pass

class Mp3FileUnitTests(TestCase):
    pass
