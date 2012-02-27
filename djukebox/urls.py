from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
                       url(r'^home/', main, name='djukebox-home'),
                       url(r'^homeframe/', album_list, name='djukebox-homeframe'),
                       url(r'^album_list/', album_list, name='djukebox-albumlist'),
                       url(r'^artist_list/', artist_list, name='djukebox-artistlist'),
                       url(r'^stream/(?P<format>\w+)/(?P<track_id>\d+)/', audio_player, name='djukebox-stream'),
                       url(r'^stream/ogg/(?P<track_id>\d+)/', audio_player, {'format': 'ogg'}, name='djukebox-stream-ogg'),
                       url(r'^stream/mp3/(?P<track_id>\d+)/', audio_player, {'format': 'mp3'}, name='djukebox-stream-mp3'),
                       url(r'^track_list/', track_list, name='djukebox-tracklist'),
                       url(r'^upload_track/', upload_track, name='djukebox-upload'),
                       url(r'^iframe_upload_track/', upload_track, {'hidden_frame': True}, name='djukebox-iframe-upload'),
                       url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'djukebox/login.html'}, name='djukebox-login'),
                       )
