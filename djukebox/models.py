from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.conf import settings

import os

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.oggvorbis import OggVorbis

class Album(models.Model):
    """The album which a track is from"""
    title = models.CharField(max_length=100)
    artist = models.ForeignKey('Artist', db_index=True)
    cover_art = models.ImageField(upload_to='djukebox/art/%Y/%m/%d/', blank=True, null=True)
    user = models.ForeignKey(User, db_index=True)
    created = models.DateTimeField(db_index=True, auto_now_add=True, blank=True)

    DEFAULT_TITLE = 'Unknown Album'
    DEFAULT_ARTIST = 'Unknown Artist'

    class Meta:
        unique_together = ['title', 'artist', 'user']

    def __unicode__(self):
        return u'%s' %self.title

    @classmethod
    def album_from_metadata(cls, audio_file):
        """Get the Album() from the audio file's metadata."""
        user = audio_file.track.user
        default_title = getattr(settings, 'DEFAULT_ALBUM_TITLE', Album.DEFAULT_TITLE)
        default_artist = getattr(settings, 'DEFAULT_ARTIST', Album.DEFAULT_ARTIST)

        album_title = (audio_file.get_album() if audio_file.get_album() != '' else default_title)
        # Try getting the album artist first
        artist_name = audio_file.get_album_artist()

        # if no album artist, set to the artist or default artist
        if artist_name == '':
            artist_name = (audio_file.get_artist() if audio_file.get_artist() else default_artist)

        # Not sure I like auto-saving a new artist here... is there a better way to do this?
        artist, created = Artist.objects.get_or_create(name=artist_name, user=user)
        album, created = cls.objects.get_or_create(title=album_title, artist=artist, user=user)
        return album

class Artist(models.Model):
    """An artist who records a track"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, db_index=True)
    created = models.DateTimeField(db_index=True, auto_now_add=True)

    DEFAULT_ARTIST = 'Unknown Artist'

    def __unicode__(self):
        return u'%s' %self.name

class AudioFile(models.Model):
    track = models.ForeignKey('Track', db_index=True)
    file = models.FileField(upload_to='djukebox/tracks/%Y/%m/%d/')
    created = models.DateTimeField(db_index=True, auto_now_add=True, blank=True)

    MP3_CONTENT_TYPES = ('audio/mp3', 'audio/mpeg')
    OGG_CONTENT_TYPES = ('audio/ogg',)

    def __unicode__(self):
        return u'%s' %self.file.name

class Mp3File(AudioFile):
    """An mp3 audio file"""
    def get_id3_data(self):
        pass

    def get_title(self):
        """Get the title from the file's id3 tag"""
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        id3 = EasyID3(file_path)
        return id3.get('title', [''])[0].strip()

    def get_artist(self):
        """Get the artist from the file's id3 tag"""
        # Should this be an object attribute rather than dong this every
        # time an attribute is needed from the id3?
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        id3 = EasyID3(file_path)
        return id3.get('performer', ['']).strip()

    def get_album(self):
        """Get the album from the file's id3 tag"""
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        id3 = EasyID3(file_path)

        return id3.get('album', [''])[0].strip()

    def get_album_artist(self):
        """Returns the album's artist from the file's id3 tag.

        Starts with id3v2.4 and works back checking fields which are used
        by that id3 version to get the album artist.
        """

        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        id3 = ID3(file_path)
        
        # These really need to default to an empty TPE2()
        if id3['TPE2'] != '':
            artist = id3.get('TPE2', None)
        else:
            artist = id3.get('TP2', None)

        # I bet this blows up, but have no test at the moment
        # artist is probably a tuple
        return artist.text[0].strip()
        

class OggFile(AudioFile):
    """An ogg-vorbis audio file"""

    # TODO: None of this has been tested at all
    def get_title(self):
        """Return the title from Vorbis comments."""
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        tags = OggVorbis(file_path)
        return tags.get('title', '').strip()

    def get_artist(self):
        """Return the artist rom Vorbis comments."""
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        tags = OggVorbis(file_path)
        return tags.get('artist', '').strip()

    def get_album(self):
        """Return the album from Vorbis comments."""
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        tags = OggVorbis(file_path)
        return tags.get('album', '').strip()

    def get_album_artist(self):
        """Return the album artist (performer) from Vorbis comments."""
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        tags = OggVorbis(file_path)
        return tags.get('performer', '').strip()

class Track(models.Model):
    """A specific audio track or song"""
    title = models.CharField(max_length=100)
    album = models.ForeignKey('Album', db_index=True, null=True, blank=True)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, db_index=True)
    created = models.DateTimeField(db_index=True, auto_now_add=True, blank=True)

    #TODO: Other attributes - genre, duration, isrc, etc.

    DEFAULT_ARTIST = 'Unknown'
    DEFAULT_TITLE = 'Unknown'

    def __unicode__(self):
        return u'%s' %self.title

def delete_audio_files(sender, **kwargs):
    audio_file = kwargs.get('instance')
    audio_file.file.delete(save=False)

post_delete.connect(delete_audio_files, sender=AudioFile)
