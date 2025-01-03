from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(client, name, args):
    """Проверяет доступность страниц для анонимного пользователя.

    Убедитесь, что страницы сайта доступны и возвращают статус 200.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(parametrized_client, name,
                                                  expected_status,
                                                  comment_id_for_args):
    """Проверяет доступность страниц редактирования и удаления комментария.

    Убедитесь, что автор может редактировать или удалять свои комментарии,
    а неавторизованный пользователь не имеет доступа.
    """
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment_id_for_args):
    """Проверяет перенаправление анонимного пользователя.

    Убедитесь, что анонимный пользователь перенаправляется на страницу входа
    при попытке редактировать или удалить комментарий.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
