"""
REST API for the Djukebox app
"""

from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, Resource

from django.conf import settings
from django.middleware.csrf import _sanitize_token, constant_time_compare
from django.utils.http import same_origin
from django.conf.urls.defaults import url

from models import Album, Artist, Track


# From tastypie 0.9.12... why write my own when this is what I'll be using asap anyway?
class SessionAuthentication(Authentication):
    """
    An authentication mechanism that piggy-backs on Django sessions.

    This is useful when the API is talking to Javascript on the same site.
    Relies on the user being logged in through the standard Django login
    setup.

    Requires a valid CSRF token.
    """
    def is_authenticated(self, request, **kwargs):
        """
        Checks to make sure the user is logged in & has a Django session.
        """
        # Cargo-culted from Django 1.3/1.4's ``django/middleware/csrf.py``.
        # We can't just use what's there, since the return values will be
        # wrong.
        # We also can't risk accessing ``request.POST``, which will break with
        # the serialized bodies.
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return request.user.is_authenticated()

        if getattr(request, '_dont_enforce_csrf_checks', False):
            return request.user.is_authenticated()

        csrf_token = _sanitize_token(request.COOKIES.get(settings.CSRF_COOKIE_NAME, ''))

        if request.is_secure():
            referer = request.META.get('HTTP_REFERER')

            if referer is None:
                return False

            good_referer = 'https://%s/' % request.get_host()

            if not same_origin(referer, good_referer):
                return False

        request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            return False

        return request.user.is_authenticated()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.
        This implementation returns the user's username.
        """
        return request.user.username

class InlineToggleMixIn(object):
    """
    Allows details=<resource> querystring param to toggle whether to return resource uri or full details
    """

    # handy dehydrate_related from
    # http://chrismeyers.org/2012/06/25/tastypie-inline-aka-nested-fulltrue-embedded-relationship-dynamically-via-get-parameter/
    def dehydrate_related(self, bundle, related_resource, *args, **kwargs):
        """
        Overrides the standard RelatedField.dehydrate_related().
        Returns the full details of a related resource if it is
        specified in the URI as if it were defined with full=True
        otherwise behaves as default, returning a URI to the related resource.
        """
        # this is not 100% ideal because the resource_name and collection_name may not be
        # what the end user sees, depending on how things are named.  They see the attribute name
        resource_name = related_resource._meta.resource_name
        collection_name = related_resource._meta.collection_name
        inlines = bundle.request.GET.get('details','').split(',')

        if resource_name in inlines or collection_name in inlines:
            bundle = related_resource.build_bundle(obj=related_resource.instance, request=bundle.request)
            return related_resource.full_dehydrate(bundle)

        # default behavior for this method
        return related_resource.get_resource_uri(bundle)

# careful with these.  If 2 resources have relationships to each
# other defined and both are some combination of ToManyFieldInlineToggle
# and ToOneFieldInlineToggle then an infinite loop can occur.
# Maybe there's a good way to limit the depth of InlineToggleMixIn?
class ToManyFieldDetailToggle(InlineToggleMixIn, fields.ToManyField):
    """ToManyField where inclusion of details inline can be toggled via the URI"""
    pass

class ToOneFieldDetailToggle(InlineToggleMixIn, fields.ToOneField):
    """ToOneField where inclusion of details inline can be toggled via the URI"""
    pass


class UserOwnedModelResource(ModelResource):
    """
    A resource which is tied to a specific user.  Users can only view and
    update resources which they own and any they create will be owned by them.
    """

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    def hydrate(self, bundle):
        bundle.obj.user = bundle.request.user

        return bundle


# to add uri specified ordering later
# http://django-tastypie.readthedocs.org/en/latest/cookbook.html#per-request-alterations-to-the-queryset

class AlbumResource(UserOwnedModelResource):
    """Tastypie resource representing djukebox.models.Album()"""

    tracks = ToManyFieldDetailToggle('djukebox.api.TrackResource', 'track_set')
    artist = ToOneFieldDetailToggle('djukebox.api.ArtistResource', 'artist', null=True)

    class Meta:
        """Meta class for AlbumResource"""

        queryset = Album.objects.all()
        resource_name = 'album'
        collection_name = 'albums'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'artist': ALL_WITH_RELATIONS,
            'title': ('exact'),
            }


class ArtistResource(UserOwnedModelResource):
    """Tastypie resource representing djukebox.models.Artist()"""

    #albums = ToManyFieldDetailToggle('djukebox.api.AlbumResource', 'album_set')

    class Meta:
        """Meta class for ArtistResource"""

        queryset = Artist.objects.all()
        resource_name = 'artist'
        collection_name = 'artists'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('exact', 'startswith'),
        }
        always_return_data = True

    # save this for later.  will break too many things to do it this way right now
    #def override_urls(self):
    #    return [
    #        url(r"^(?P<resource_name>%s)/(?P<name>[\s\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
    #    ]


class TrackResource(UserOwnedModelResource):
    """Tastypie resource representing djukebox.models.Track()"""

    album = ToOneFieldDetailToggle('djukebox.api.AlbumResource', 'album')
    artist = ToOneFieldDetailToggle('djukebox.api.ArtistResource', 'artist', null=True)

    class Meta:
        """Meta class for TrackResource"""

        queryset = Track.objects.all()
        resource_name = 'track'
        collection_name = 'tracks'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'delete', 'patch']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('exact', 'startswith'),
            'album': ALL_WITH_RELATIONS,
            'album__artist': ALL_WITH_RELATIONS,
            'artist': ALL_WITH_RELATIONS
            }

    def dehydrate(self, bundle):

        # add stream urls to the track detail.  It seems like
        # this should be able to be exposed some other way
        # based on http://django-tastypie.readthedocs.org/en/v0.9.11/cookbook.html
        # which says this is only needed for data that is not an attribute
        # or method on the model
        bundle.data['mp3_stream_url'] = bundle.obj.mp3_stream_url()
        bundle.data['ogg_stream_url'] = bundle.obj.ogg_stream_url()
        return bundle


from .forms import AlbumEditForm, TrackEditForm
from django.db import transaction
class TrackAlbumResource(Resource):
    """
    A special resource for posting title and artist for both track
    and album in one shot so that multiple round trip http
    requests are not required to determine if the correct artist and
    album already exist.
    Provides a denormalized abstraction over the highly normalized db
    which is modeled in most of the resources.
    """

    track_artist = fields.CharField()
    track_title = fields.CharField()
    album_artist = fields.CharField()
    album_title = fields.CharField()

    class Meta:
        resource_name = 'track_album'
        detail_uri_name = 'pk'
        detail_allowed_methods = ['get', 'patch']
        authentication = SessionAuthentication()
        authorization = Authorization()
        object_class = Track

    def obj_get(self, bundle, request=None, **kwargs):
        # ModelResource actually calls obj_get_list which does a bunch
        # of stuff and returns a queryset of Track.objects.filter()
        # and then obj_get returns the first of those if length == 1
        # otherwise raises exceptions.  For now I am keeping this simple
        # and only doing exactly what I need right now.

        return Track.objects.get(**kwargs)

    @transaction.commit_on_success
    def obj_update(self, bundle, request=None, **kwargs):
        bundle = self.full_hydrate(bundle)

        # I suspect there's a better place to do this, before it even gets put in the bundle
        # but for now this place is obvious to me and works for my exact needs at the moment
        album_data = AlbumEditForm({'artist': bundle.data['album_artist'],
                                    'title': bundle.data['album_title']})
        track_data = TrackEditForm({'artist': bundle.data['track_artist'],
                                    'title': bundle.data['track_title']})

        if album_data.is_valid() and track_data.is_valid():
            album_artist, created = Artist.objects.get_or_create(user_id=request.user.pk,
                                                                 name__iexact=album_data.cleaned_data['artist'],
                                                                 defaults={'name': album_data.cleaned_data['artist']})

            album, created = Album.objects.get_or_create(user_id=request.user.pk,
                                                         title__iexact=album_data.cleaned_data['title'],
                                                         artist_id=album_artist.pk,
                                                         defaults={'title': album_data.cleaned_data['title']})

            if track_data.cleaned_data['artist'].lower() == album_artist.name.lower():
                track_artist = album_artist
            else:
                track_artist, created = Artist.objects.get_or_create(user_id=request.user.pk,
                                                                     name__iexact=track_data.cleaned_data['artist'],
                                                                     defaults={'name': track_data.cleaned_data['artist']})

            # Track object ownership is being checked/managed here.  I'm sure there's a better way such as
            # how the ModelResources handle it
            Track.objects.filter(pk=kwargs['pk'], user_id=request.user.pk).update(artist=track_artist,
                                                                                  album=album,
                                                                                  title=track_data.cleaned_data['title'])

        return bundle
