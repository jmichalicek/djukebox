import os
import subprocess
import logging
from django.conf import settings
from models import AudioFile, Mp3File, OggFile

logger = logging.getLogger(__name__)

# Find a way to make this work with files stored on cloudfiles/s3/etc.
class ConverterBase(object):
    """Base class for audio converters."""

    # if __init__ is defined and takes an AudioFile object
    # then several more lines of duplicate code can be removed
    # but a single converter instance could not convert
    # several files.  Does it matter?

    def _get_target_filename(self, source_path, extension):
        
        # Takes full file path of setings.MEDIA_ROOT/whatever/file.ext
        # where /whatever/ is the upload_to attribute on the FileField
        # and returns that same path with the extension changed
        # This seems really convoluted... since upload_to is dynamic
        # I'm not sure there's a more straightforward way, though.
        directory, name = os.path.split(source_path)
        name, ext = os.path.splitext(name)
        return os.path.join(directory, '%s.%s' %(name, extension))
        

    # or should this take an actual file object like the ogg_file
    def _save(self, file_class, source_file, target_filename):
        media_directory = os.path.dirname(source_file.file.name)
        new_file = file_class(track=source_file.track)
        new_file.file.name = os.path.join(media_directory, os.path.basename(target_filename))
        new_file.full_clean()
        new_file.save()

        return new_file

    def convert(self, audio_file):
        """Not implemented."""
        raise NotImplementedError


class AvconvOggToMp3(ConverterBase):
    """Create mp3 files from ogg files using avconv"""

    def convert(self, ogg_file):
        source_path = os.path.join(settings.MEDIA_ROOT, ogg_file.file.name)
        target_filename = self._get_target_filename(source_path, 'mp3')

        logger.debug('Converting %s to %s using avconv' %(source_path, target_filename))
        subprocess.call([settings.DJUKEBOX_AVCONV_BIN, '-i', source_path, target_filename])

        logger.debug('Finished encoding.  Saving AudioFile')
        return self._save(Mp3File, ogg_file, target_filename)


class FFMpegOggToMp3(ConverterBase):
    """Create mp3 files from ogg files using FFMpeg."""

    def convert(self, ogg_file):
        source_path = os.path.join(settings.MEDIA_ROOT, ogg_file.file.name)
        target_filename = self._get_target_filename(source_path, 'mp3')

        logger.debug('Converting %s to %s using ffmpeg' %(source_path, target_filename))
        #TODO: Use Kenneth Reitz' module for subprocess handling
        subprocess.call([settings.DJUKEBOX_FFMPEG_BIN, '-i', source_path, target_filename])

        logger.debug('Finished encoding.  Saving AudioFile')
        return self._save(Mp3File, ogg_file, target_filename)


class SoxOggToMp3(ConverterBase):
    """Create mp3 files from ogg files using sox"""

    # ogg_file is an OggFile.  Any AudioFile or subclass should work
    # as long as the actual file is an ogg
    def convert(self, ogg_file):
        source_path = os.path.join(settings.MEDIA_ROOT, ogg_file.file.name)
        target_filename = self._get_target_filename(source_path, 'mp3')

        logger.debug('Converting %s to %s using sox' %(source_path, target_filename))
        subprocess.call([settings.DJUKEBOX_SOX_BIN, source_path, target_filename])

        logger.debug('Finished encoding.  Saving AudioFile')
        return self._save(Mp3File, ogg_file, target_filename)

class AvconvMp3ToOgg(ConverterBase):
    """Create ogg files from mp3 files using avconv."""
    def convert(self, mp3_file):
        source_path = os.path.join(settings.MEDIA_ROOT, mp3_file.file.name)
        target_filename = self._get_target_filename(source_path, extension='ogg')

        logger.debug('Converting %s to %s using avconv' %(source_path, target_filename))
        subprocess.call([settings.DJUKEBOX_AVCONV_BIN, '-i', source_path, '-acodec', 'libvorbis',
                         '-ac', '2', target_filename])

        logger.debug('Finished encoding.  Saving AudioFile')
        return self._save(OggFile, mp3_file, target_filename)


class FFMpegMp3ToOgg(ConverterBase):
    """Create ogg files from mp3 files using ffmpeg"""
    def convert(self, mp3_file):
        source_path = os.path.join(settings.MEDIA_ROOT, mp3_file.file.name)
        target_filename = self._get_target_filename(source_path, extension='ogg')

        logger.debug('Converting %s to %s using ffmpeg' %(source_path, target_filename))
        subprocess.call([settings.DJUKEBOX_FFMPEG_BIN, '-i', source_path, '-acodec', 'vorbis', 
                         '-ac', '2', target_filename])

        logger.debug('Finished encoding.  Saving AudioFile')
        return self._save(OggFile, mp3_file, target_filename)

class SoxMp3ToOgg(ConverterBase):
    """Create ogg files from mp3 files using sox"""
    def convert(self, mp3_file):
        source_path = os.path.join(settings.MEDIA_ROOT, mp3_file.file.name)
        #oga is really correct, but sox doesn't like oga
        target_filename = self._get_target_filename(source_path, extension='ogg')

        logger.debug('Converting %s to %s using sox' %(source_path, target_filename))
        subprocess.call([settings.DJUKEBOX_SOX_BIN, source_path, target_filename])
        logger.debug('Finished encoding.  Saving AudioFile')
        return self._save(OggFile, mp3_file, '-t ogg', target_filename)
