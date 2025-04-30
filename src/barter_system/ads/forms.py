from django import forms

from .constans import DEFAULT_IMG_URL
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):

    class Meta:
        model = Ad
        exclude = ['user', 'created_at', 'is_available']

    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url')
        if not image_url:
            image_url = DEFAULT_IMG_URL
            return image_url
        image_url = image_url.lower()
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        for ext in valid_extensions:
            if image_url.endswith(ext):
                return image_url
        raise forms.ValidationError(
            'URL должен вести к изображению с одним из следующих '
            'расширений: .jpg, .jpeg, .png, .gif, .bmp, .tiff.')


class ExchangeProposalFormBase(forms.ModelForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.full_clean()
        if commit:
            instance.save()
        return instance


class ExchangeProposalFormCreate(ExchangeProposalFormBase):
    class Meta:
        model = ExchangeProposal
        fields = ['comment']

    def __init__(self, *args, **kwargs):
        self.ad_sender_pk = kwargs.pop('ad_sender_pk', None)
        self.ad_receiver_pk = kwargs.pop('ad_receiver_pk', None)
        super().__init__(*args, **kwargs)

        if self.ad_sender_pk and self.ad_receiver_pk:
            self.instance.ad_sender = Ad.objects.get(pk=self.ad_sender_pk)
            self.instance.ad_receiver = Ad.objects.get(pk=self.ad_receiver_pk)


class ExchangeProposalFormUpdate(ExchangeProposalFormBase):
    class Meta:
        model = ExchangeProposal
        fields = ['status']

    def __init__(self, *args, **kwargs):
        self.exc_pk = kwargs.pop('exc_pk', None)
        super().__init__(*args, **kwargs)

        if self.exc_pk:
            exc_obj = ExchangeProposal.objects.get(pk=self.exc_pk)
            self.instance.ad_sender = exc_obj.ad_sender
            self.instance.ad_receiver = exc_obj.ad_receiver
