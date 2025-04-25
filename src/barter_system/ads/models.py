from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


from .constans import (
    AD_TITLE_MAX_LENGTH, STATUS_CHOICES, AD_IMAGE_URL_MAX_LENGTH,
    CATEGORY_CHOICES, CONDITION_CHOICES)


User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        abstract = True


class Ad(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField('Название', max_length=AD_TITLE_MAX_LENGTH)
    description = models.TextField('Описание', blank=True, default='')
    image_url = models.URLField(
        'Изображение', max_length=AD_IMAGE_URL_MAX_LENGTH, blank=True,
        default='')
    category = models.CharField(
        'Категория', choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField(
        'Состояние', choices=CONDITION_CHOICES)


class ExchangeProposal(BaseModel):
    ad_sender = models.ForeignKey(
        Ad, on_delete=models.SET_NULL, null=True,
        related_name='exchange_senders')
    ad_receiver = models.ForeignKey(
        Ad, on_delete=models.SET_NULL, null=True,
        related_name='exchange_receivers')
    comment = models.TextField('Комментарий', blank=True, default='')
    status = models.CharField(
        'Статус', choices=STATUS_CHOICES, default='pending')

    def clean(self):
        if not self.ad_sender or not self.ad_receiver:
            raise ValidationError(
                'Оба объявления должны быть указаны для обмена.')

        if self.ad_sender.user == self.ad_receiver.user:
            raise ValidationError(
                'Невозможно обменивать объявления одного пользователя.')

        return super().clean()
