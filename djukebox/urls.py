from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
                       url(r'^home/', main, name='djukebox-home'),
                       url(r'^homeframe/', album_list, name='djukebox-homeframe'),
                       url(r'^stream_list/(?P<track_id>\d+)/', track_stream_list, name='djukebox-list-streams'),
                       # the following stream_list/ cannot be used directly, but can be used by {% url %} tags in
                       # templated javascript to get the base url when you don't know the track id yet
                       url(r'^stream_list/', track_stream_list, name='djukebox-list-streams'),
                       url(r'^album/(?P<album_id>\d+)/', album_songs, name='djukebox-album'), 
                       url(r'^album_list/', album_list, name='djukebox-albumlist'),
                       url(r'^artist/(?P<artist_id>\d+)/', artist_discography, name='djukebox-artist'),
                       url(r'^artist_list/', artist_list, name='djukebox-artistlist'),
                       url(r'^stream/(?P<format>\w+)/(?P<track_id>\d+)/', audio_player, name='djukebox-stream'),
                       url(r'^stream/ogg/(?P<track_id>\d+)/', audio_player, {'format': 'ogg'}, name='djukebox-stream-ogg'),
                       url(r'^stream/mp3/(?P<track_id>\d+)/', audio_player, {'format': 'mp3'}, name='djukebox-stream-mp3'),
                       url(r'^track_list/', track_list, name='djukebox-tracklist'),
                       url(r'^upload_track/', upload_track, name='djukebox-upload'),
                       url(r'^iframe_upload_track/', upload_track, {'hidden_frame': True}, name='djukebox-iframe-upload'),
                       url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'djukebox/login.html'}, name='djukebox-login'),
                       )
