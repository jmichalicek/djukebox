"""
REST API for the Djukebox app
"""

from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from django.conf import settings
from django.middleware.csrf import _sanitize_token, constant_time_compare
from django.utils.http import same_origin

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
    def dehydrate_related(self, bundle, related_resource):
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


# to add uri specified ordering later
# http://django-tastypie.readthedocs.org/en/latest/cookbook.html#per-request-alterations-to-the-queryset


class AlbumResource(ModelResource):
    """Tastypie resource representing djukebox.models.Album()"""

    tracks = ToManyFieldDetailToggle('djukebox.api.TrackResource', 'track_set')
    artist = ToOneFieldDetailToggle('djukebox.api.ArtistResource', 'artist')

    class Meta:
        """Meta class for AlbumResource"""

        queryset = Album.objects.all()
        resource_name = 'album'
        collection_name = 'albums'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'artist': ALL_WITH_RELATIONS,
            }

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    def alter_list_data_to_serialize(self, request, data):
        data['albums'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['albums']
        del data['albums']
        return data


class ArtistResource(ModelResource):
    """Tastypie resource representing djukebox.models.Artist()"""

    #albums = ToManyFieldDetailToggle('djukebox.api.AlbumResource', 'album_set')

    class Meta:
        """Meta class for ArtistResource"""

        queryset = Artist.objects.all()
        resource_name = 'artist'
        collection_name = 'artists'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('exact', 'startswith'),
        }

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    #tastypie 0.9.12 will use Meta.collection_name properly so that
    #this doesn't need to be done to name the collection something
    #other than "objects"
    def alter_list_data_to_serialize(self, request, data):
        data['artists'] = data['objects']
        del data['objects']
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['artists']
        del data['artists']
        return data


class TrackResource(ModelResource):
    """Tastypie resource representing djukebox.models.Track()"""

    album = ToOneFieldDetailToggle('djukebox.api.AlbumResource', 'album')

    class Meta:
        """Meta class for TrackResource"""

        queryset = Track.objects.all()
        resource_name = 'track'
        collection_name = 'tracks'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'name': ('exact', 'startswith'),
            'album': ALL_WITH_RELATIONS,
            'album__artist': ALL_WITH_RELATIONS
            }

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    def alter_list_data_to_serialize(self, request, data):
        data['tracks'] = data['objects']
        del data['objects']
        return data

    def dehydrate(self, bundle):

        # add stream urls to the track detail.  It seems like
        # this should be able to be exposed some other way
        # based on http://django-tastypie.readthedocs.org/en/v0.9.11/cookbook.html
        # which says this is only needed for data that is not an attribute
        # or method on the model
        bundle.data['mp3_stream_url'] = bundle.obj.mp3_stream_url()
        bundle.data['ogg_stream_url'] = bundle.obj.ogg_stream_url()
        return bundle
