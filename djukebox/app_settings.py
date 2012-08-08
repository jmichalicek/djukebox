from django.conf import settings

AVCONV_BIN = getattr(settings, 'DJUKEBOX_AVCONV_BIN', '/usr/bin/avconv') #where it lives in debian
CONVERT_UPLOADS = getattr(settings, 'DJUKEBOX_CONVERT_UPLOADS', True)
DEFAULT_ALBUM_TITLE = getattr(settings, 'DJUKEBOX_DEFAULT_ALBUM_TITLE', 'Unknown Album')
DEFAULT_TRACK_TITLE = getattr(settings, 'DJUKEBOX_DEFAULT_TRACK_TITLE', 'Unknown Track')
DEFAULT_ARTIST = getattr(settings, 'DJUKEBOX_DEFAULT_ARTIST', 'Unknown Artist')
FFMPEG_BIN = getattr(settings, 'DJUKEBOX_FFMPEG_BIN', '/usr/bin/ffmpeg') # Where it lives in debian
MP3_CONTENT_TYPES = getattr(settings, 'DJUKEBOX_MP3_CONTENT_TYPES', ('audio/mpeg', 'audio/mp3'))
OGG_CONTENT_TYPES = getattr(settings, 'DJUKEBOX_OGG_CONTENT_TYPES', ('audio/ogg', 'audio/oga'))
SOX_BIN = getattr(settings, 'DJUKEBOX_SOX_BIN', '/usr/bin/sox') # Where it lives in debian
UPLOAD_FILE_MAX_SIZE = getattr(settings, 'DJUKEBOX_UPLOAD_FILE_MAX_SIZE', 10000000) #arbitrary big enough file size for testing
UPLOAD_FILE_TYPES = getattr(settings, 'DJUKEBOX_UPLOAD_FILE_TYPES', ('audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/oga'))
USE_MEDIA_URL = getattr(settings, 'DJUKEBOX_USE_MEDIA_URL', False)

# Would like to handle these in a better way to more easily allow other file types
# to be uploaded and then converted to ogg and mp3.
OGG_TO_MP3 = getattr(settings, 'DJUKEBOX_OGG_TO_MP3', 'djukebox.converters.FFMpegOggToMp3')
MP3_TO_OGG = getattr(settings, 'DJUKEBOX_MP3_TO_OGG', 'djukebox.converters.FFMpegMp3ToOgg')
