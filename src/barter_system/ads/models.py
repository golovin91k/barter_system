from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError


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
    description = models.TextField('Описание')
    image_url = models.URLField(
        'Ссылка на изображение', max_length=AD_IMAGE_URL_MAX_LENGTH,
        blank=True)
    category = models.CharField(
        'Категория', choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField(
        'Состояние', choices=CONDITION_CHOICES)

    is_available = models.BooleanField(default=True)  # Новое поле


class ExchangeProposal(BaseModel):
    ad_sender = models.ForeignKey(
        Ad, on_delete=models.SET_NULL, null=True,
        related_name='exchange_senders')
    ad_receiver = models.ForeignKey(
        Ad, on_delete=models.SET_NULL, null=True,
        related_name='exchange_receivers')
    comment = models.TextField('Комментарий')
    status = models.CharField(
        'Статус', choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ad_sender', 'ad_receiver'],
                name='unique_exchange_pair')]

    def clean(self):
        if not self.ad_sender or not self.ad_receiver:
            raise ValidationError(
                'Объявления отправителя и получателя должны быть заданы!')

        if self.ad_sender == self.ad_receiver:
            raise ValidationError(
                'Нельзя обменяться на одно и то же объявление.')

        if (not self.ad_sender.is_available or
                not self.ad_receiver.is_available):
            raise ValidationError(
                'Нельзя обменяться на недоступное объявление.')

        if ExchangeProposal.objects.filter(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver
        ).exclude(id=self.id).exists():
            raise ValidationError('Такой обмен уже существует.')

        if ExchangeProposal.objects.filter(
            ad_sender=self.ad_receiver,
            ad_receiver=self.ad_sender
        ).exclude(id=self.id).exists():
            raise ValidationError(
                'Зеркальный обмен этими объявлениями уже существует.')

        return self
