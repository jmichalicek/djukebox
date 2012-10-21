from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
#from tastypie.authentication import SessionAuthentication
#from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource
from models import Album, Artist, Track


class InlineToggleMixIn(object):
    """
    Allows inline=true querystring param to toggle whether to return resource uri or full details
    """

    # handy dehydrate_related from
    # http://chrismeyers.org/2012/06/25/tastypie-inline-aka-nested-fulltrue-embedded-relationship-dynamically-via-get-parameter/
    def dehydrate_related(self, bundle, related_resource):

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
    pass

class ToOneFieldDetailToggle(InlineToggleMixIn, fields.ToOneField):
    pass


# to add uri specified ordering later
# http://django-tastypie.readthedocs.org/en/latest/cookbook.html#per-request-alterations-to-the-queryset


class AlbumResource(ModelResource):
    tracks = ToManyFieldDetailToggle('djukebox.api.TrackResource', 'track_set')
    artist = ToOneFieldDetailToggle('djukebox.api.ArtistResource', 'artist')

    class Meta:
        queryset = Album.objects.all()
        resource_name = 'album'
        collection_name = 'albums'
        list_allowed_methods=['get']
        detail_allowed_methods=['get']
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
    #albums = ToManyFieldDetailToggle('djukebox.api.AlbumResource', 'album_set')

    class Meta:
        queryset = Artist.objects.all()
        resource_name = 'artist'
        collection_name = 'artists'
        list_allowed_methods=['get']
        detail_allowed_methods=['get']
#        authentication = SessionAuthentication()
#        authorization = Authorization()
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
    album = ToOneFieldDetailToggle('djukebox.api.AlbumResource', 'album')

    class Meta:
        queryset = Track.objects.all()
        resource_name = 'track'
        collection_name = 'tracks'
        list_allowed_methods=['get']
        detail_allowed_methods=['get']
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