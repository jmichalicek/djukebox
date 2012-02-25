from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
                       url(r'^home/', main, name='djukebox-home'),
                       url(r'^homeframe/', album_list, name='djukebox-homeframe'),
                       url(r'^album_list/', album_list, name='djukebox-albumlist'),
                       url(r'^artist_list/', artist_list, name='djukebox-artistlist'),
                       url(r'^track_list/', track_list, name='djukebox-tracklist'),
                       url(r'^upload_track/', upload_track, name='djukebox-upload'),
                       url(r'^iframe_upload_track/', upload_track, {'hidden_frame': True}, name='djukebox-iframe-upload'),
                       url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'djukebox/login.html'}, name='djukebox-login'),
                       )
