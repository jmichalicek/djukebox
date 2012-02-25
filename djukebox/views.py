from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_control, cache_page
from django.http import Http404, HttpResponseRedirect, HttpResponse

from models import Album, Artist, Track
from forms import SimpleTrackUploadForm


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

    if request.method == 'POST':
        track = Track(user=request.user)
        upload_form = SimpleTrackUploadForm(request.POST, request.FILES, instance=track)
        if upload_form.is_valid():
            track = upload_form.save()
            track.title = 'Test Track'
            track.save()
            if hidden_frame == False:
                return HttpResponseRedirect(reverse('djukebox-homeframe'))
            else:
                return HttpResponse('{"track_upload": {"status": "sucess", "title": "%s"}}' %track.title, mimetype='application/javascript')

        if hidden_frame == True:
            return HttpResponse('{"track_upload": {"status": "error"}}', mimetype='application/javascript')

    else:
        upload_form = SimpleTrackUploadForm()

    return render_to_response(
        'djukebox/upload_track.html',
        {'upload_form': upload_form},
        context_instance=RequestContext(request)
    )
