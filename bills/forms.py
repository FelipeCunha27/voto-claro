from django import forms
from bills.models import Submission
from django.core.exceptions import ValidationError

class SubmissionForm(forms.ModelForm):
    # Declarando os campos explicitamente para remover o required=True do HTML
    official_source_url = forms.URLField(
        required=False, 
        label='Link Oficial (Opcional)'
    )
    source_text = forms.CharField(
        widget=forms.Textarea, 
        required=False, 
        label='Texto do Projeto (Cole aqui se não tiver o arquivo)'
    )
    uploaded_file = forms.FileField(
        required=False, 
        label='Arquivo PDF'
    )

    class Meta:
        model = Submission
        fields = ['official_source_url', 'source_text', 'uploaded_file']
        
    def clean(self):
        cleaned_data = super().clean()
        source_text = cleaned_data.get('source_text')
        uploaded_file = cleaned_data.get('uploaded_file')
        official_source_url = cleaned_data.get('official_source_url')
        
        # A validação real acontece aqui no backend
        if not source_text and not uploaded_file and not official_source_url:
            raise ValidationError("Por favor, preencha pelo menos um dos campos: Link, Texto ou Arquivo PDF.")
            
        return cleaned_data
