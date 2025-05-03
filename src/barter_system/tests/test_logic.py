from http import HTTPStatus  # noqa

from pytest_django.asserts import assertRedirects
from django.urls import reverse
import pytest
from ads.models import Ad, ExchangeProposal


def test_user_can_create_ad(author_client, author, ad_form_data):
    url = reverse('ads:add_ad')
    author_client.post(url, data=ad_form_data)
    assert Ad.objects.count() == 1
    new_ad = Ad.objects.get()
    assert new_ad.title == ad_form_data['title']
    assert new_ad.description == ad_form_data['description']
    assert new_ad.category == ad_form_data['category']
    assert new_ad.condition == ad_form_data['condition']
    assert new_ad.is_available == ad_form_data['is_available']
    assert new_ad.user == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_ad(client, ad_form_data):
    url = reverse('ads:add_ad')
    response = client.post(url, data=ad_form_data)
    login_url = reverse('login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Ad.objects.count() == 0


def test_author_can_edit_ad(author, author_client, ad_form_data, ad):
    url = reverse('ads:update_ad', args=(ad.pk,))
    author_client.post(url, ad_form_data)
    ad.refresh_from_db()
    assert ad.title == ad_form_data['title']
    assert ad.description == ad_form_data['description']
    assert ad.category == ad_form_data['category']
    assert ad.condition == ad_form_data['condition']
    assert ad.is_available == ad_form_data['is_available']
    assert ad.user == author


@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
def test_ad_sender_user_can_create_exc(
        ad_sender_user_client, ad_sender, ad_receiver):
    """Проверка, что пользователь может создать обмен,
    если оба объявления доступны для обмена."""

    url = reverse('ads:add_exc', args=(ad_receiver.pk, ad_sender.pk))
    exc_form_data = {
        'ad_sender': ad_sender,
        'ad_receiver': ad_receiver,
        'comment': 'давай обменяемся вещами'}
    ad_sender_user_client.post(url, data=exc_form_data)
    assert ExchangeProposal.objects.count() == 1
    new_exc = ExchangeProposal.objects.get()
    assert new_exc.ad_sender == exc_form_data['ad_sender']
    assert new_exc.ad_sender == exc_form_data['ad_sender']
    assert new_exc.comment == exc_form_data['comment']
    assert new_exc.status == 'pending'


@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [False], indirect=True)
def test_ad_sender_user_cant_create_exc(
        ad_sender_user_client, ad_sender, ad_receiver):
    """Проверка, что пользователь НЕ может создать обмен,
    если одно из объявлений не доступно для обмена."""

    url = reverse('ads:add_exc', args=(ad_receiver.pk, ad_sender.pk))
    exc_form_data = {
        'ad_sender': ad_sender,
        'ad_receiver': ad_receiver,
        'comment': 'давай обменяемся вещами'}
    ad_sender_user_client.post(url, data=exc_form_data)
    assert ExchangeProposal.objects.count() == 0


@pytest.mark.parametrize('ad_receiver', [False], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
def test_ad_sender_user_cant_create_exc_(
        ad_sender_user_client, ad_sender, ad_receiver):
    """Проверка, что пользователь НЕ может создать обмен,
    если одно из объявлений не доступно для обмена.
    Зеркальная проверка."""

    url = reverse('ads:add_exc', args=(ad_receiver.pk, ad_sender.pk))
    exc_form_data = {
        'ad_sender': ad_sender,
        'ad_receiver': ad_receiver,
        'comment': 'давай обменяемся вещами'}
    ad_sender_user_client.post(url, data=exc_form_data)
    assert ExchangeProposal.objects.count() == 0


@pytest.mark.parametrize('exc_is_pending', ['pending'], indirect=True)
@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
def test_ad_receiver_user_can_update_exc(
        ad_receiver_user_client, exc_is_pending):
    """Проверка, что пользователь, который получил заявку на обмен,
    сможет рассмотреть её, то есть изменить статус обмена."""

    exc_form_data = {'status': 'accepted'}
    url = reverse('ads:update_exc', args=(exc_is_pending.pk,))
    ad_receiver_user_client.post(url, data=exc_form_data)
    exc_is_pending.refresh_from_db()
    assert exc_is_pending.status == 'accepted'
    assert exc_is_pending.ad_sender.is_available is False
    assert exc_is_pending.ad_receiver.is_available is False


@pytest.mark.parametrize('exc_is_pending', ['accepted'], indirect=True)
@pytest.mark.parametrize('ad_receiver', [False], indirect=True)
@pytest.mark.parametrize('ad_sender', [False], indirect=True)
def test_ad_receiver_user_can_update_exc_(
        ad_receiver_user_client, exc_is_pending):
    """Проверка, что пользователь, который рассмотрел заявку на обмен,
    НЕ сможет рассмотреть её повторно."""

    exc_form_data = {'status': 'rejected'}
    url = reverse('ads:update_exc', args=(exc_is_pending.pk,))
    ad_receiver_user_client.post(url, data=exc_form_data)
    exc_is_pending.refresh_from_db()
    assert exc_is_pending.status == 'accepted'
    assert exc_is_pending.ad_sender.is_available is False
    assert exc_is_pending.ad_receiver.is_available is False


@pytest.mark.parametrize('exc_is_pending', ['pending'], indirect=True)
@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
def test_ad_sender_user_cant_update_exc(
        ad_sender_user_client, exc_is_pending):
    """Проверка, что пользователь, который направил заявку на обмен,
    НЕ сможет рассмотреть её самостоятельно"""

    exc_form_data = {'status': 'accepted'}
    url = reverse('ads:update_exc', args=(exc_is_pending.pk,))
    ad_sender_user_client.post(url, data=exc_form_data)
    exc_is_pending.refresh_from_db()
    assert exc_is_pending.status == 'pending'
    assert exc_is_pending.ad_sender.is_available is True
    assert exc_is_pending.ad_receiver.is_available is True
