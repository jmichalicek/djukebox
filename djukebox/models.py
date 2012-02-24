from django import models

class Album(models.Model):
    """The album which a track is from"""
    title = models.CharField(max_length=100)
    artist = models.ForeignKey('Artist', db_index=True)

    def __unicode__(self):
        return u'%s' %self.title

class Artist(models.Model):
    """An artist who records a track"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' %self.name

class Track(models.Model):
    """A specific audio track or song"""
    title = models.CharField(max_length=100)
    album = models.ForeignKey('Album', db_index=True)
    track_number = models.PostiveIntegerField(null=True, blank=True)

    #TODO: Other attributes - genre, duration, isrc, etc.

    def __unicode__(self):
        return u'%s' %self.name
