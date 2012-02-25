from django import forms
from models import Track

class SimpleTrackUploadForm(forms.ModelForm):
    asset = forms.FileField(label='Select a song to upload')
    class Meta:
        model = Track
        exclude = ('title', 'album', 'track_number', 'user')
