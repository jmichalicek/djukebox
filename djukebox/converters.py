import os
import subprocess
from django.conf import settings
from models import AudioFile

class DjukeboxMp3FromOgg():
    """Create mp3 files from ogg files."""
    def convert(self, ogg_file):
        media_directory = os.path.dirname(ogg_file.file.name)
        source_path = os.path.join(settings.MEDIA_ROOT, ogg_file.file.name)

        directory, name = os.path.split(source_path)
        name, extension = os.path.splitext(name)
        target_filename = os.path.join(directory, '%s.mp3' %name)

        # pysox was corrupting files so revert to command line tools
        # run based on the settings.py settings below. ffmpeg creates a smaller file
        # but changes command line options frequently and occasionally libs
        # so no promises it'll work
        #DJUKEBOX_AUDIO_ENCODER = 'sox' # or 'ffmpeg'
        #DJUKEBOX_SOX_BIN = '/usr/bin/sox'
        #DJUKEBOX_FFMPEG_BIN = '/usr/bin/ffmpeg'

        if settings.DJUKEBOX_AUDIO_ENCODER == 'sox':
            subprocess.call([settings.DJUKEBOX_SOX_BIN, source_path, target_filename])
        if settings.DJUKEBOX_AUDIO_ENCODER == 'ffmpeg':
            # have not tested this yet.
            subprocess.call([settings.DJUKEBOX_FFMPEG_BIN, '-i', source_path, target_filename])

        new_file = AudioFile(track=ogg_file.track)
        new_file.file.name = os.path.join(media_directory, os.path.basename(target_filename))
        new_file.full_clean()
        new_file.save()

        return new_file

class DjukeboxOggFromMp3():
    """Create ogg files from mp3 files."""
    def convert(self, mp3_file):
        media_directory = os.path.dirname(mp3_file.file.name)
        source_path = os.path.join(settings.MEDIA_ROOT, mp3_file.file.name)

        directory, name = os.path.split(source_path)
        name, extension = os.path.splitext(name)
        target_filename = os.path.join(directory, '%s.ogg' %name)

        # pysox was corrupting files so revert to command line tools
        # run based on the settings.py settings below. ffmpeg creates a smaller file
        # but changes command line options frequently and occasionally libs
        # so no promises it'll work
        #DJUKEBOX_AUDIO_ENCODER = 'sox' # or 'ffmpeg'
        #DJUKEBOX_SOX_BIN = '/usr/bin/sox'
        #DJUKEBOX_FFMPEG_BIN = '/usr/bin/ffmpeg'

        if settings.DJUKEBOX_AUDIO_ENCODER == 'sox':
            subprocess.call([settings.DJUKEBOX_SOX_BIN, source_path, target_filename])
        if settings.DJUKEBOX_AUDIO_ENCODER == 'ffmpeg':
            # have not tested this yet.
            subprocess.call([settings.DJUKEBOX_FFMPEG_BIN, '-i', source_path, '-acodec', 'vorbis', target_filename])

        new_file = AudioFile(track=mp3_file.track)
        new_file.file.name = os.path.join(media_directory, os.path.basename(target_filename))
        new_file.full_clean()
        new_file.save()

        return new_file

