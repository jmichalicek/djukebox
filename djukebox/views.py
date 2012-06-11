from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import transaction
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control, cache_page
from django.http import Http404, HttpResponseRedirect, HttpResponse

from models import Album, Artist, Track, AudioFile, OggFile, Mp3File
from forms import TrackUploadForm
from tasks import convert_file_to_ogg, convert_file_to_mp3

import os
import mimetypes
import logging
import simplejson

logger = logging.getLogger(__name__)

@login_required
def track_stream_list(request, track_id=None):
    """Return available stream urls for a track."""

    # Does it matter if it's ajax currently?
    if request.is_ajax():
        track = get_object_or_404(Track, id=track_id, user=request.user)
        json_response_data = {}

        # Do this the simplest way for now.  Will be troublesome if there's a reason to play
        # some other file type.
        try:
            mp3 = Mp3File.objects.get(track=track)
            json_response_data['mp3'] = mp3.get_stream_url()
        except ObjectDoesNotExist:
            json_response_data['mp3'] = ''

        try:
            ogg = OggFile.objects.get(track=track)
            json_response_data['ogg'] = ogg.get_stream_url()
        except ObjectDoesNotExist:
            json_response_data['ogg'] = ''

        return HttpResponse(simplejson.dumps(json_response_data), mimetype='application/json')

@login_required
def album_songs(request, album_id):
    """View displaying the tracks on an album"""
    album = get_object_or_404(Album, id=album_id, user=request.user)
    tracks = Track.objects.filter(album=album)

    return render_to_response(
        'djukebox/album_songs.html',
        {'album': album,
         'tracks': tracks},
        context_instance=RequestContext(request)
        )

@login_required
def album_list(request):
    """View providing a list of a user's albums"""
    albums = Album.objects.filter(user=request.user)

    return render_to_response(
        'djukebox/album_list.html',
        {'albums': albums,},
        context_instance=RequestContext(request)
        )


@login_required
def artist_list(request):
    """View providing a list of a user's artists."""
    artists = Artist.objects.filter(user=request.user)

    return render_to_response(
        'djukebox/artist_list.html',
        {'artists': artists,},
        context_instance=RequestContext(request)
        )

@login_required
def artist_discography(request, artist_id):
    """View providing a list of songs and albums by a specific artist."""
    
    artist = get_object_or_404(Artist, id=artist_id)
    albums = Album.objects.filter(artist=artist)

    return render_to_response(
        'djukebox/discography.html',
        {'artist': artist,
         'albums': albums},
        context_instance=RequestContext(request)
        )

@cache_control(no_cache=True)
@login_required
def stream_track(request, track_id, format):
    # TODO: Rename this to stream_track?
    # format is a callable, the class of audio file to play such as Mp3File or OggFile
    track = get_object_or_404(format, track__id=track_id, track__user=request.user)
    file_path = os.path.join(settings.MEDIA_ROOT, track.file.name)
    # ogg files encoded with pysox seem to be getting a media type of (audio/ogg, none) as a tuple
    # which throws off firefox when it gets the content-type header.  Opera is ok with it, though.
    # As a fix I am just grabbing the first one here which seems to always work
    resp = HttpResponse(FileIterWrapper(open(file_path,"rb")), mimetype=mimetypes.guess_type(file_path)[0])
    resp['Content-Length'] = os.path.getsize(file_path)
    resp['Content-Disposition'] = 'filename=' + os.path.basename(file_path)  
    return resp

@login_required
def genre_list(request):
    """View providing a list of a user's genres."""
    pass

@login_required
def track_list(request):
    """View providing a list of a user's tracks."""

    # TODO: Need a nice way to paginate or buffer this without interrupting the user
    tracks = Track.objects.filter(user=request.user)

    return render_to_response(
        'djukebox/track_list.html',
        {'tracks': tracks,},
        context_instance=RequestContext(request)
    )

@login_required
def main(request):
    
    return render_to_response(
        'djukebox/main.html',
        {},
        context_instance=RequestContext(request)
    )

@login_required
@transaction.commit_on_success
def upload_track(request, hidden_frame=False):
    # TODO: break this up into smaller functions
    # TODO: this needs to deal with re-encoding tracks as mp3 and ogg and the Track model
    # probably also needs updated to deal with this
    if request.method == 'POST':
        upload_form = TrackUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            default_track_title = getattr(settings, 'DJUKEBOX_DEFAULT_TRACK_TITLE', Track.DEFAULT_TITLE)
            default_artist = getattr(settings, 'DJUKEBOX_DEFAULT_ARTIST', Artist.DEFAULT_ARTIST)

            track = Track(user=request.user)
            track.title = default_track_title
            track.full_clean()
            track.save()

            mp3_content_types = getattr(settings, 'DJUKEBOX_MP3_CONTENT_TYPES', Mp3File.DEFAULT_CONTENT_TYPES)
            ogg_content_types = getattr(settings, 'DJUKEBOX_OGG_CONTENT_TYPES', OggFile.DEFAULT_CONTENT_TYPES)

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
            if mimetype not in settings.DJUKEBOX_UPLOAD_FILE_TYPES:
                # Delete the Track and AudioFile and return an error
                json_response_data = '{"track_upload": {"status": "error", "error": "invalid file type %s"}}' %mimetype
                audio_file.delete()
                track.delete()
                logger.warn('mimetypes.guess_type detected different content type than http header specified')
            elif getattr(settings, 'DJUKEBOX_CONVERT_UPLOADS', True):
                if mimetype in ogg_content_types:
                    convert_file_to_mp3.delay(audio_file.id)
                elif mimetype in mp3_content_types:
                    convert_file_to_ogg.delay(audio_file.id)

                logger.debug('Successfully uploaded track %s with id %s' %(track.title, track.id))
                json_response_data = '{"track_upload": {"status": "sucess", "title": "%s"}}' %track.title

        else:
            # Get the errors in a cleaner way
            logger.debug('{"track_upload": {"status": "error", "errors": %s}}' %upload_form.errors)
            json_response_data = '{"track_upload": {"status": "error", "errors": %s}}' %upload_form.errors


        if hidden_frame == True:
            return HttpResponse(json_response_data, mimetype='application/javascript')
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
