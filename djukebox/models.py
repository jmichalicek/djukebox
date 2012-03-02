from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.conf import settings

import os

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

    def __unicode__(self):
        return u'%s' %self.file.name

class Track(models.Model):
    """A specific audio track or song"""
    title = models.CharField(max_length=100)
    album = models.ForeignKey('Album', db_index=True, null=True, blank=True)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, db_index=True)

    #TODO: Other attributes - genre, duration, isrc, etc.

    def __unicode__(self):
        return u'%s' %self.title

def delete_audio_files(sender, **kwargs):
    audio_file = kwargs.get('instance')
    audio_file.file.delete(save=False)

post_delete.connect(delete_audio_files, sender=AudioFile)

