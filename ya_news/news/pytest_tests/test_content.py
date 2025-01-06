import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(news_list, client):
    """
    На главной странице отображается количество новостей, соответствующее
    настройке NEWS_COUNT_ON_HOME_PAGE.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    """На главной странице новости сортируются по дате в порядке убывания."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments):
    """
    Комментарии к новости сортируются по времени создания в порядке
    возрастания.
    """
    url = reverse('news:detail', args=(news.id,))
    client.get(url)
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    """
    Анонимный пользователь не видит форму для добавления комментариев на
    странице новости.
    """
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, news_id_for_args):
    """
    Авторизованный пользователь видит форму для добавления комментариев на
    странице новости.
    """
    url = reverse('news:detail', args=news_id_for_args)
    response = not_author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
