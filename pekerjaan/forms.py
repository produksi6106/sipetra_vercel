from django import forms
from .models import PekerjaanMitra

class PekerjaanForm(forms.ModelForm):
    class Meta:
        model = PekerjaanMitra
        fields = '__all__'
