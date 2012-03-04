from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control, cache_page
from django.http import Http404, HttpResponseRedirect, HttpResponse

from models import Album, Artist, Track, AudioFile, OggFile, Mp3File
from forms import TrackUploadForm
from tasks import convert_file_to_ogg


import os
import mimetypes

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
    albums = Album.objects.filter(user=request.user)

    return render_to_response(
        'djukebox/artist_list.html',
        {'albums': albums,},
        context_instance=RequestContext(request)
    )


@cache_control(no_cache=True)
@login_required
def audio_player(request, track_id, format):
    # This is obviously a terrible way to get the correct file format.  A format attribute will probably be added
    # to the AudioFile model
    if format.lower() == 'mp3':
        track = get_object_or_404(Mp3File, track__id=track_id, track__user=request.user)
    elif format.lower() == 'ogg':
        track = get_object_or_404(OggFile, track__id=track_id, track__user=request.user)

    file_path = os.path.join(settings.MEDIA_ROOT, track.file.name)
    # ogg files encoded with pysox seem to be getting a media type of (audio/ogg, none) as a tuple
    # which throws off firefox when it gets the content-type header.  Opera is ok with it, though.
    # As a fix I am just grabbing the first one here
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
def upload_track(request, hidden_frame=False):

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

            file_data = upload_form.cleaned_data['file']
            # TODO: Add more flexibility for user to specify mp3 and ogg content types?
            if file_data.content_type in AudioFile.MP3_CONTENT_TYPES:
                audio_file = Mp3File(file=file_data)
            if file_data.content_type in AudioFile.OGG_CONTENT_TYPES:
                audio_file = OggFile(file=file_data)

            audio_file.track = track
            audio_file.full_clean()
            audio_file.save()

            # Now that the physical file has been written, read the metadata
            track.title = (audio_file.get_title() if audio_file.get_title != '' else default_track_title)

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
            if mimetype not in settings.DJUKEBOX_UPLOAD_FILE_TYPES:
                # Delete the Track and AudioFile and return an error
                json_response_data = '{"track_upload": {"status": "error", "error": "invalid file type %s"}}' %mimetype
                audio_file.delete()
                track.delete()
            else:
                if mimetype == 'audio/ogg':
                    create_mp3_file(track=track, ogg_file=audio_file)
                elif mimetype in ('audio/mp3', 'audio/mpeg'):
                    convert_file_to_ogg.delay(audio_file.id)
                    # TODO: make this dependent upon settings.py settings

                #success!
                json_response_data = '{"track_upload": {"status": "sucess", "title": "%s"}}' %track.title

        else:
            # Get the errors in a cleaner way
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
