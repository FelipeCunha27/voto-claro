from django import forms
from bills.models import Submission
from django.core.exceptions import ValidationError

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'origin_body', 'bill_number', 'bill_year', 'official_source_url', 'source_text', 'uploaded_file']
        
    def clean(self):
        cleaned_data = super().clean()
        source_text = cleaned_data.get('source_text')
        uploaded_file = cleaned_data.get('uploaded_file')
        
        if not source_text and not uploaded_file:
            raise ValidationError("Você deve fornecer o texto original ou enviar um arquivo.")
        if source_text and uploaded_file:
            raise ValidationError("Forneça apenas o texto ou um arquivo, não ambos.")
            
        return cleaned_data
