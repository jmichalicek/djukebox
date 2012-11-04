"""
Djukebox Views
"""

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import transaction
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponseRedirect, HttpResponse

from models import Album, Track, OggFile, Mp3File
from forms import TrackUploadForm
from tasks import convert_file_to_ogg, convert_file_to_mp3
import app_settings

import os
import mimetypes
import logging

logger = logging.getLogger(__name__)

@cache_control(no_cache=True)
@login_required
def stream_track(request, track_id, file_format):
    """Stream out the audio file for a track"""

    # TODO: Rename this to stream_track?
    # file_format is a callable, the class of audio file to play such as Mp3File or OggFile
    track = get_object_or_404(file_format, track__id=track_id, track__user=request.user)
    file_path = os.path.join(settings.MEDIA_ROOT, track.file.name)
    # ogg files encoded with pysox seem to be getting a media type of (audio/ogg, none) as a tuple
    # which throws off firefox when it gets the content-type header.  Opera is ok with it, though.
    # As a fix I am just grabbing the first one here which seems to always work
    resp = HttpResponse(FileIterWrapper(open(file_path,"rb")), mimetype=mimetypes.guess_type(file_path)[0])
    resp['Content-Length'] = os.path.getsize(file_path)
    resp['Content-Disposition'] = 'filename=' + os.path.basename(file_path)
    return resp

@login_required
def main(request):
    """The primary Djukebox view which renders the UI"""

    return render_to_response(
        'djukebox/main.html',
        {'content_view': reverse('djukebox-home')},
        context_instance=RequestContext(request)
    )

@cache_control(no_cache=True)
@login_required
@transaction.commit_on_success
def upload_track(request, hidden_frame=False):
    """Handle the upload of an audio file and create a new Track()"""

    # TODO: break this up into smaller functions
    # TODO: this needs to deal with re-encoding tracks as mp3 and ogg and the Track model
    # probably also needs updated to deal with this

    if request.method == 'POST':
        upload_form = TrackUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            default_track_title = app_settings.DEFAULT_TRACK_TITLE
            default_artist = app_settings.DEFAULT_ARTIST

            track = Track(user=request.user)
            track.title = default_track_title
            track.full_clean()
            track.save()

            mp3_content_types = app_settings.MP3_CONTENT_TYPES
            ogg_content_types = app_settings.OGG_CONTENT_TYPES

            file_data = upload_form.cleaned_data['file']
            # TODO: Add more flexibility for user to specify mp3 and ogg content types?
            if file_data.content_type in mp3_content_types:
                logger.debug('mp3 file was uploaded')
                audio_file = Mp3File(file=file_data)
            if file_data.content_type in ogg_content_types:
                logger.debug('ogg file was uploaded')
                audio_file = OggFile(file=file_data)

            audio_file.track = track
            audio_file.full_clean()
            audio_file.save()

            # Now that the physical file has been written, read the metadata
            new_title = audio_file.get_title()
            track.title = (new_title if new_title != '' else default_track_title)

            album = Album.album_from_metadata(audio_file)
            album.full_clean()
            album.save()

            track.album = album
            track.full_clean()
            track.save()

            #TODO: Set artist on Track()

            # Now that this is saved, make sure the file really is a valid filetype
            # and kill it if it's not.  The track upload form validates the http content-type header
            # but does not actually check the file.
            mimetype = mimetypes.guess_type(os.path.join(settings.MEDIA_ROOT, audio_file.file.name))[0]

            # Check allowed file types first.  We may want to only allow certain types
            # even if the system can support others.
            # Windows is annoying and sends video/ogg if the file extension is .ogg
            # and audio/ogg if it's .oga even though the standard says .ogg is for audio
            # according to wikipedia "Since 2007, the Xiph.Org Foundation recommends that .ogg only be
            # used for Ogg Vorbis audio files"

            # TODO: Use messages framework for these track upload success/fail messages
            # as well as get celery tasks to do that. https://github.com/codeinthehole/django-async-messages maybe?
            # ...or write my own for fun.
            if mimetype in app_settings.UPLOAD_FILE_TYPES:
                if app_settings.CONVERT_UPLOADS:
                    if mimetype in ogg_content_types:
                        convert_file_to_mp3.delay(audio_file.id)
                    elif mimetype in mp3_content_types:
                        convert_file_to_ogg.delay(audio_file.id)

                logger.debug('Successfully uploaded track {0} with id {1}'.format(track.title, track.id))
                json_response_data = {'track_upload': {'status': 'success', 'title': track.title}}
            else:
                # Delete the Track and AudioFile and return an error
                json_response_data = '{"track_upload": {"status": "error", "error": "invalid file type %s"}}' % mimetype
                audio_file.delete()
                track.delete()
                logger.warn('mimetypes.guess_type detected different content type than http header specified')
        else:
            # Get the errors in a cleaner way
            logger.debug('{"track_upload": {"status": "error", "errors": %s}}' % upload_form.errors)
            json_response_data = {'track_upload': {'status': 'error', 'errors': upload_form.errors.values()}}


        if hidden_frame == True:
            import json
            return HttpResponse(json.dumps(json_response_data), mimetype='application/javascript')
        else:
            # On the off chance the upload is not being posted to an iframe so that it can happen asynchronously
            # where is a sane place to redirect to?
            return HttpResponseRedirect(reverse('djukebox-homeframe'))

    else:
        upload_form = TrackUploadForm()

    return render_to_response(
        'djukebox/upload_track.html',
        {'upload_form': upload_form},
        context_instance=RequestContext(request)
    )


# This should possibly go elsewhere
# Grabbed it from http://metalinguist.wordpress.com/2008/02/12/django-file-and-stream-serving-performance-gotcha/
class FileIterWrapper(object):
    """Read a file in chunks with iter and next rather than until next newline"""
    def __init__(self, flo, chunk_size = 1024**2):
        self.flo = flo
        self.chunk_size = chunk_size

    def next(self):
        data = self.flo.read(self.chunk_size)
        if data:
            return data
        else:
            raise StopIteration

    def __iter__(self):
        return self
