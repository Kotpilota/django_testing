import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(news_list, client):
    """Проверяет количество новостей на главной странице."""
    # Arrange: Подготовка URL
    url = reverse('news:home')

    # Act: Запрос страницы
    response = client.get(url)
    object_list = response.context['object_list']

    # Assert: Проверка количества новостей
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    """Сортировка новостей по дате в убывающем порядке."""
    # Arrange: Подготовка URL
    url = reverse('news:home')

    # Act: Запрос страницы
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]

    # Assert: Проверка порядка сортировки
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments):
    """Сортировка комментариев по времени создания в порядке возрастания."""
    # Arrange: Подготовка URL
    url = reverse('news:detail', args=(news.id,))

    # Act: Запрос страницы и извлечение комментариев
    client.get(url)
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]

    # Assert: Проверка порядка сортировки
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    """Анонимный пользователь не видит форму добавления комментариев."""
    # Arrange: Подготовка URL
    url = reverse('news:detail', args=news_id_for_args)

    # Act: Запрос страницы
    response = client.get(url)

    # Assert: Проверка отсутствия формы
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, news_id_for_args):
    """Авторизованный пользователь видит форму добавления комментариев."""
    # Arrange: Подготовка URL
    url = reverse('news:detail', args=news_id_for_args)

    # Act: Запрос страницы
    response = not_author_client.get(url)

    # Assert: Проверка наличия формы и её типа
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
