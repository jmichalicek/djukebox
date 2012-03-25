from django.contrib import admin
from models import *

class TrackAdmin(admin.ModelAdmin):
    model = Track
    list_filter = ('album', 'album__artist')

class AlbumAdmin(admin.ModelAdmin):
    model = Album
    list_filter = ('artist', )

admin.site.register(Album, AlbumAdmin)
admin.site.register(AudioFile)
admin.site.register(Artist)
admin.site.register(Mp3File)
admin.site.register(OggFile)
admin.site.register(Track, TrackAdmin)
