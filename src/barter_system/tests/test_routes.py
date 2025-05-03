from http import HTTPStatus

import pytest
from django.urls import reverse

from ads.models import Ad # noqa


@pytest.mark.parametrize('exc_is_pending', ['pending'], indirect=True)
@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
@pytest.mark.parametrize(
    'name, expected_status',
    (
        ('ads:list_ads', HTTPStatus.OK),
        ('ads:add_ad', HTTPStatus.FOUND),
        ('ads:detail_ad', HTTPStatus.OK),
        ('ads:update_ad', HTTPStatus.FOUND),
        ('ads:delete_ad', HTTPStatus.FOUND),
        ('ads:user_available_ads', HTTPStatus.FOUND),
        ('ads:add_exc', HTTPStatus.FOUND),
        ('ads:list_excs', HTTPStatus.OK),
        ('ads:update_exc', HTTPStatus.FOUND),
        ('ads:delete_exc', HTTPStatus.FOUND),
        ('ads:user_ads', HTTPStatus.FOUND),
        ('ads:user_excs', HTTPStatus.FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(
        client, name, expected_status, ad, ad_receiver, ad_sender,
        exc_is_pending):
    if name in ('ads:detail_ad', 'ads:update_ad', 'ads:delete_ad',
                'ads:user_available_ads'):
        url = reverse(name, args=(ad.pk,))
    elif name in ('ads:add_exc'):
        url = reverse(name, args=(ad_receiver.pk, ad_sender.pk))
    elif name in ('ads:update_exc', 'ads:delete_exc'):
        url = reverse(name, args=(exc_is_pending.pk,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == expected_status

@pytest.mark.parametrize('exc_is_pending', ['pending'], indirect=True)
@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
@pytest.mark.parametrize(
    'name, expected_status',
    (
        ('ads:add_ad', HTTPStatus.OK),
        ('ads:user_available_ads', HTTPStatus.OK),
        ('ads:add_exc', HTTPStatus.OK),
        ('ads:update_exc', HTTPStatus.OK),
        ('ads:delete_exc', HTTPStatus.FORBIDDEN),
        ('ads:user_ads', HTTPStatus.OK),
        ('ads:user_excs', HTTPStatus.OK),
    ),
)
def test_pages_availability_for_user(
        name, expected_status, ad, ad_receiver, ad_sender,
        exc_is_pending, user_client):
    if name in ('ads:user_available_ads',):
        url = reverse(name, args=(ad.pk,))
    elif name in ('ads:add_exc'):
        url = reverse(name, args=(ad_receiver.pk, ad_sender.pk))
    elif name in ('ads:update_exc', 'ads:delete_exc'):
        url = reverse(name, args=(exc_is_pending.pk,))
    else:
        url = reverse(name)
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'client_name, expected_status',
    (
        ('not_author_client', HTTPStatus.NOT_FOUND),
        ('author_client', HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('ads:update_ad', 'ads:delete_ad'),
)
def test_ads_pages_availability_for_different_users(
    request, client_name, name, ad, expected_status
):
    client = request.getfixturevalue(client_name)
    url = reverse(name, args=(ad.pk,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('exc_is_pending', ['pending'], indirect=True)
@pytest.mark.parametrize('ad_receiver', [True], indirect=True)
@pytest.mark.parametrize('ad_sender', [True], indirect=True)
@pytest.mark.parametrize(
    'client_name, expected_status',
    (
        ('ad_receiver_user_client', HTTPStatus.FORBIDDEN),
        ('ad_sender_user_client', HTTPStatus.OK),
    ),
)
def test_delete_exc_page_availability_for_different_users(
    request, client_name, expected_status, exc_is_pending
):
    client = request.getfixturevalue(client_name)
    url = reverse('ads:delete_exc', args=(exc_is_pending.pk,))
    response = client.get(url)
    assert response.status_code == expected_status
