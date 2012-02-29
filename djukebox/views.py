from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control, cache_page
from django.http import Http404, HttpResponseRedirect, HttpResponse

from models import Album, Artist, Track, AudioFile
from forms import SimpleTrackUploadForm

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
    track = get_object_or_404(AudioFile, track__id=track_id, track__user=request.user, file__icontains=format)

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
        upload_form = SimpleTrackUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            audio_file = upload_form.save(commit=False)
            track = Track(user=request.user)
            track.title = 'Test Track'
            track.full_clean()
            track.save()

            audio_file.track = track
            audio_file.full_clean()
            audio_file.save()

            ####### encode ogg ####
            from tasks import convert_file_to_ogg
            convert_file_to_ogg.delay(audio_file.id)
            # TODO: make this dependent upon settings.py settings

            if hidden_frame == False:
                return HttpResponseRedirect(reverse('djukebox-homeframe'))
            else:
                return HttpResponse('{"track_upload": {"status": "sucess", "title": "%s"}}' %track.title, mimetype='application/javascript')

        if hidden_frame == True:
            return HttpResponse('{"track_upload": {"status": "error", "errors": %s}}' %upload_form.errors, mimetype='application/javascript')

    else:
        upload_form = SimpleTrackUploadForm()

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
