from django import forms

from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):

    class Meta:
        model = Ad
        exclude = ['user', 'created_at']

    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url')
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        if not any(
                image_url.lower().endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError(
                'URL должен вести к изображению с одним из следующих '
                'расширений: .jpg, .jpeg, .png, .gif, .bmp, .tiff.')


class ExchangeProposalForm(forms.ModelForm):

    class Meta:
        model = ExchangeProposal
        exclude = ['created_at']
