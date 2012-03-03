import os
import subprocess
import importlib
import logging
from django.conf import settings
from celery.task import task
from models import AudioFile, Mp3File, OggFile

DEFAULT_OGG_TO_MP3 = 'djukebox.converters.DjukeboxMp3FromOgg'
DEFAULT_MP3_TO_OGG = 'djukebox.converters.DjukeboxOggFromMp3'

logger = logging.getLogger(__name__)

# TODO: provide rate limiting options
@task
def convert_file_to_ogg(file_id):
    # TODO: make sure the file isn't already an ogg
    try:
        cls = settings.DJUKEBOX_OGG_CREATOR
    except AttributeError:
        cls = DEFAULT_MP3_TO_OGG

    logger.debug('Creating ogg from mp3 with module %s' %cls)

    converter = class_from_string(cls)()

    mp3_file = Mp3File.objects.get(id=file_id)
    logger.debug('Begin encoding ogg from AudioFile id %s' %mp3_file.id)
    ogg_file = converter.convert(mp3_file)
    logger.debug('Finished encoding ogg.  Created AudioFile id %s' %ogg_file.id)

    return ogg_file

@task
def convert_file_to_mp3(file_id):
    try:
        cls = settings.DJUKEBOX_MP3_CREATOR
    except AttributeError:
        cls = DEFAULT_OGG_TO_MP3

    logger.debug('Creating ogg from mp3 with module %s' %cls)

    converter = class_from_string(cls)()

    ogg_file = OggFile.objects.get(id=file_id)
    logger.debug('Begin encoding mp3 from AudioFile id %s' %ogg_file.id)
    mp3_file = converter.convert(ogg_file)
    logger.debug('Finished encoding mp3.  Created AudioFile id %s' %mp3_file.id)

    return mp3_file

def class_from_string(class_string):
    """Takes a string package. Class and returns the class object"""

    class_package = class_string.split('.')
    module = '.'.join(class_package[:-1])
    c = getattr(importlib.import_module(module), class_package[-1])

    return c
