import os
import subprocess
from django.conf import settings
from celery.task import task
from models import AudioFile

DEFAULT_OGG_TO_MP3 = 'djukebox.converters.DjukeboxMp3FromOgg'
DEFAULT_MP3_TO_OGG = 'djukebox.converters.DjukeboxOggFromMp3'

# TODO: provide rate limiting options
@task
def convert_file_to_ogg(file_id):
    # TODO: make sure the file isn't already an ogg
    try:
        cls = settings.DJUKEBOX_OGG_CREATOR
    except AttributeError:
        cls = DEFAULT_MP3_TO_OGG

    converter = class_from_string(cls)()

    mp3_file = AudioFile.objects.get(id=file_id)
    ogg_file = converter.convert(mp3_file)

    return ogg_file

@task
def convert_file_to_mp3(file_id):
    try:
        cls = settings.DJUKEBOX_MP3_CREATOR
    except AttributeError:
        cls = DEFAULT_OGG_TO_MP3

    converter = class_from_string(cls)()

    ogg_file = AudioFile.objects.get(id=file_id)
    mp3_file = converter.convert(ogg_file)

    return mp3_file

def class_from_string(class_string):
    """Takes a string package.Class and returns an instance of the class"""

    class_package = class_string.split('.')
    module = '.'.join(class_package[:-1])
    m = __import__(module)
    # m is just the top level module

    for p in class_package[1:]:
        m  = getattr(m, p)

    return m
