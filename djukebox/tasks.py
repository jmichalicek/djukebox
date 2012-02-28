import os
import subprocess
from django.conf import settings
from celery.task import task
from models import AudioFile


# TODO: provide rate limiting options
@task
def convert_file_to_ogg(file_id):
    # TODO: make sure the file isn't already an ogg

    source_file = AudioFile.objects.get(id=file_id)
    media_directory = os.path.dirname(source_file.file.name)
    source_path = os.path.join(settings.MEDIA_ROOT, source_file.file.name)

    directory, name = os.path.split(source_path)
    name, extension = os.path.splitext(name)
    wav_name = os.path.join(directory, '%s.wav' %name)
    target_filename = os.path.join(directory, '%s.ogg' %name)


    # TODO: Make this a factory/pluggable deal so that users can
    # write their own encoding script and plug it in if they want

    # pysox was corrupting files so revert to command line tools
    # run based on the settings.py settings below.  ffmpeg creates a smaller file
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

    new_file = AudioFile(track=source_file.track)
    new_file.file.name = os.path.join(media_directory, os.path.basename(target_filename))
    new_file.full_clean()
    new_file.save()
