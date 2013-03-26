"""
Forms for Djukebox
"""

from django import forms
from django.template.defaultfilters import filesizeformat

from djukebox.app_settings import UPLOAD_FILE_MAX_SIZE, UPLOAD_FILE_TYPES
from djukebox.models import Track


class TrackUploadForm(forms.Form):
    """Form for uploading an audio file to create a Track()"""

    file = forms.FileField(label='Select a song to upload')

    def clean_file(self):
        """
        Overrides default forms.Form.clean_file()
        Checks to make sure the file is an appropriate file type and size
        """

        #from http://stackoverflow.com/a/4855340
        data = self.cleaned_data['file']
        if data:
            # This comes from the http headers.  They could be lying.
            # Be sure to validate the actual file after saving as well.
            file_type = data.content_type

            if len(data.name.split('.')) == 1:
                raise forms.ValidationError('File type is not supported')

            if file_type in UPLOAD_FILE_TYPES:
                if data._size > UPLOAD_FILE_MAX_SIZE:
                    raise forms.ValidationError('Please keep filesize under %s. Current filesize %s' % (filesizeformat(UPLOAD_FILE_MAX_SIZE), filesizeformat(data._size)))
            else:
                raise forms.ValidationError('File type is not supported: %s' %file_type)
        return data

class TrackEditForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    artist = forms.CharField(max_length=100, required=False)

class AlbumEditForm(forms.Form):
    title = forms.CharField(max_length=100, required=False, label='Album Title')
    artist = forms.CharField(max_length=100, required=False, label='Album Artist')
