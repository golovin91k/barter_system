import pytest
from django.test.client import Client

from ads.models import Ad, ExchangeProposal


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='user')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def ad_sender_user(django_user_model):
    return django_user_model.objects.create(username='ad_sender_user')


@pytest.fixture
def ad_receiver_user(django_user_model):
    return django_user_model.objects.create(username='ad_receiver_user')


@pytest.fixture
def user_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def ad_sender_user_client(ad_sender_user):
    client = Client()
    client.force_login(ad_sender_user)
    return client


@pytest.fixture
def ad_receiver_user_client(ad_receiver_user):
    client = Client()
    client.force_login(ad_receiver_user)
    return client


@pytest.fixture
def ad(author):
    ad = Ad.objects.create(
        user=author,
        title='iphone 16',
        description='Почти новый айфон, только один раз упал.',
        image_url='https://i.ytimg.com/vi/h3BKjZMGoIw/maxresdefault.jpg',
        category='electronics',
        condition='used',
        is_available=True)
    return ad


@pytest.fixture
def ad_receiver(ad_receiver_user, request):
    is_available = request.param
    ad = Ad.objects.create(
        user=ad_receiver_user,
        title='iphone 16',
        description='Почти новый айфон, только один раз упал.',
        image_url='https://i.ytimg.com/vi/h3BKjZMGoIw/maxresdefault.jpg',
        category='electronics',
        condition='used',
        is_available=is_available)
    return ad


@pytest.fixture
def ad_sender(ad_sender_user, request):
    is_available = request.param
    ad = Ad.objects.create(
        user=ad_sender_user,
        title='Ipad',
        description='Новый айпэд.',
        image_url='',
        category='electronics',
        condition='new',
        is_available=is_available)
    return ad


@pytest.fixture
def exc_is_pending(ad_receiver, ad_sender, request):
    status = request.param
    exc = ExchangeProposal.objects.create(
        ad_sender=ad_sender,
        ad_receiver=ad_receiver,
        comment='Давай меняться!',
        status=status)
    return exc


@pytest.fixture
def ad_form_data():
    return {
        'title': 'Новый заголовок',
        'description': 'Новое описание',
        'image_url': 'https://i.ytimg.com/vi/h3BKjZMGoIw/maxresdefault.jpg',
        'category': 'other',
        'condition': 'new',
        'is_available': True}
