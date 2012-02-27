from django import forms
from models import AudioFile

class SimpleTrackUploadForm(forms.ModelForm):
    file = forms.FileField(label='Select a song to upload')
    class Meta:
        model = AudioFile
        exclude = ('user', 'track')
