from django import forms
from .models import Record
from .models import Rating

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['title', 'artist', 'genre', 'release_date', 'rating', 'review']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'rating': forms.NumberInput(attrs={'min': '1', 'max': '10'}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['cd', 'rating_value', 'review']
        widgets = {
            'rating_value': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }
