from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

# TODO: For many test cases there needs to be either some audio files included or something which will generate a dummy audio files.

class MainViewTests(TestCase):
    """Test cases for views.home"""

    def setUp(self):
        self.old_login = settings.LOGIN_URL
        settings.LOGIN_URL = '/djukebox/login/'
        self.user = User.objects.create_user('test', 'test@example.com', 'test')
        
    def tearDown(self):
        settings.LOGIN_URL = self.old_login

    def test_logged_in(self):
        """Access the main view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get('/djukebox/home/')
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the main view when not logged in"""
        response = self.client.get('/djukebox/home/')
        self.assertRedirects(response, '/djukebox/login/?next=/djukebox/home/')
        
class AlbumListViewTests(TestCase):
    """Test cases for views.album_list"""

    def setUp(self):
        self.old_login = settings.LOGIN_URL
        settings.LOGIN_URL = '/djukebox/login/'
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def tearDown(self):
        settings.LOGIN_URL = self.old_login

    def test_logged_in(self):
        """Access the album view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get('/djukebox/album_list/')
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the album_list view when not logged in"""
        response = self.client.get('/djukebox/album_list/')
        self.assertRedirects(response, '/djukebox/login/?next=/djukebox/album_list/')

class ArtistListViewTests(TestCase):
    """Test cases for views.artist_list"""

    def setUp(self):
        self.old_login = settings.LOGIN_URL
        settings.LOGIN_URL = '/djukebox/login/'
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def tearDown(self):
        settings.LOGIN_URL = self.old_login

    def test_logged_in(self):
        """Access the artist_list view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get('/djukebox/artist_list/')
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the main view when not logged in"""
        response = self.client.get('/djukebox/artist_list/')
        self.assertRedirects(response, '/djukebox/login/?next=/djukebox/artist_list/')

class TrackListViewTests(TestCase):
    """Test cases for views.track_list"""

    def setUp(self):
        self.old_login = settings.LOGIN_URL
        settings.LOGIN_URL = '/djukebox/login/'
        self.user = User.objects.create_user('test', 'test@example.com', 'test')

    def tearDown(self):
        settings.LOGIN_URL = self.old_login

    def test_logged_in(self):
        """Access the track_list view while logged in"""
        self.client.login(username='test', password='test')
        response = self.client.get('/djukebox/track_list/')
        self.assertEqual(response.status_code, 200)

    def test_logged_out(self):
        """Access the track_list view when not logged in"""
        response = self.client.get('/djukebox/track_list/')
        self.assertRedirects(response, '/djukebox/login/?next=/djukebox/track_list/')
