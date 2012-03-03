from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.conf import settings

import os

from mutagen.easyid3 import EasyID3

class Album(models.Model):
    """The album which a track is from"""
    title = models.CharField(max_length=100)
    artist = models.ForeignKey('Artist', db_index=True)
    cover_art = models.ImageField(upload_to='djukebox/art/%Y/%m/%d/')
    user = models.ForeignKey(User, db_index=True)

    def __unicode__(self):
        return u'%s' %self.title

class Artist(models.Model):
    """An artist who records a track"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, db_index=True)

    def __unicode__(self):
        return u'%s' %self.name

class AudioFile(models.Model):
    track = models.ForeignKey('Track', db_index=True)
    file = models.FileField(upload_to='djukebox/tracks/%Y/%m/%d/')

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
        file_path = os.path.join(setting.MEDIA_ROOT, self.file.name)
        id3 = EasyID3(file_path)
        return id3['title']

    def get_artist(self):
        """Get the artist from the file's id3 tag"""
        # Should this be an object attribute rather than dong this every
        # time an attribute is needed from the id3?
        file_path = os.path.join(setting.MEDIA_ROOT, self.file.name)
        id3 = EasyID3(file_path)
        return id3['performer']

    def get_album(self):
        """Get the album from the file's id3 tag"""
        file_path = os.path.join(setting.MEDIA_ROOT, self.file.name)
        id3 = EasyID3(file_path)
        return id3['album']

class OggFile(AudioFile):
    """An ogg-vorbis audio file"""
    def get_title(self):
        pass

    def get_artist(self):
        pass

    def get_album(self):
        pass


class Track(models.Model):
    """A specific audio track or song"""
    title = models.CharField(max_length=100)
    album = models.ForeignKey('Album', db_index=True, null=True, blank=True)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, db_index=True)

    #TODO: Other attributes - genre, duration, isrc, etc.

    DEFAULT_ARTIST = 'Unknown'
    DEFAULT_TITLE = 'Unknown'

    def __unicode__(self):
        return u'%s' %self.title

def delete_audio_files(sender, **kwargs):
    audio_file = kwargs.get('instance')
    audio_file.file.delete(save=False)

post_delete.connect(delete_audio_files, sender=AudioFile)
