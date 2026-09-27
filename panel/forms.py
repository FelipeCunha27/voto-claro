from django import forms
from bills.models import Flag

class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ['excerpt', 'description']
        labels = {
            'excerpt': 'Trecho do problema (opcional)',
            'description': 'Descrição do problema (campo obrigatório)',
        }
