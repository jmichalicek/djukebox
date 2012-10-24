from django.conf.urls.defaults import *
from tastypie.api import Api, NamespacedApi

#from views import *
from models import Mp3File, OggFile
from api import *

# There must be a better way
v1_api = NamespacedApi(api_name='v1', urlconf_namespace='djukeboxapi')
v1_api.register(ArtistResource())
v1_api.register(AlbumResource())
v1_api.register(TrackResource())

urlpatterns = patterns('',
                       url(r'^api/', include(v1_api.urls)),
                       url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'djukebox/login.html'}, name='djukebox-login'),
                       url(r'^logout/', 'django.contrib.auth.views.logout_then_login', name="djukebox-logout"),
                       )

urlpatterns += patterns('djukebox.views',
                       url(r'^home/', 'main', name='djukebox-home'),
                       # the following stream_list/ cannot be used directly, but can be used by {% url %} tags in
                       # templated javascript to get the base url when you don't know the track id yet
                       url(r'^stream/(?P<format>\w+)/(?P<track_id>\d+)/', 'stream_track', name='djukebox-stream'),
                       url(r'^stream/ogg/(?P<track_id>\d+)/', 'stream_track', {'format': OggFile}, name='djukebox-stream-ogg'),
                       url(r'^stream/mp3/(?P<track_id>\d+)/', 'stream_track', {'format': Mp3File}, name='djukebox-stream-mp3'),
                       url(r'^upload_track/', 'upload_track', name='djukebox-upload'),
                       url(r'^iframe_upload_track/', 'upload_track', {'hidden_frame': True}, name='djukebox-iframe-upload'),
                       url(r'^$', 'main', name='djukebox-root')
                       )
