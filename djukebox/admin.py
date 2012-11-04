"""
django.contrib.admin classes and registration for Djukebox
"""
from django.contrib import admin
from models import Album, AudioFile, Artist, Mp3File, OggFile, Track

class TrackAdmin(admin.ModelAdmin):
    """ModelAdmin for Track()"""
    model = Track
    list_filter = ('album', 'album__artist')

class AlbumAdmin(admin.ModelAdmin):
    """ModelAdmin for Album()"""
    model = Album
    list_filter = ('artist', )

admin.site.register(Album, AlbumAdmin)
admin.site.register(AudioFile)
admin.site.register(Artist)
admin.site.register(Mp3File)
admin.site.register(OggFile)
admin.site.register(Track, TrackAdmin)
