from django import forms
from .models import Record
from .models import Rating

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['cd', 'user_rating', 'review']
        widgets = {
            'user_rating': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cd'].label_from_instance = lambda obj: f"{obj.title} by {obj.artist}"


class RatingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['record'].queryset = Record.objects.filter(user=user)

    class Meta:
        model = Rating
        fields = ['record', 'rating_value', 'review']
        widgets = {
            'rating_value': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }
