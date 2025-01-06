from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')

@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')

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
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )

@pytest.fixture
def news_id_for_args(news):
    return (news.id,)

@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )

@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)

@pytest.fixture
def news_list():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

@pytest.fixture
def comments(news, author):
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        ) for index in range(10)
    ]
    Comment.objects.bulk_create(comments)

@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария',
    }
