from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['title', 'artist', 'genre', 'release_date', 'rating', 'review']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'rating': forms.NumberInput(attrs={'min': '1', 'max': '10'}),
        }
