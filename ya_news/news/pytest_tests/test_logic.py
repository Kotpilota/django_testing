from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, form_data, news_id_for_args
):
    """Анонимный пользователь не может создать комментарий."""
    # Arrange
    url = reverse('news:detail', args=news_id_for_args)

    # Act
    client.post(url, data=form_data)

    # Assert
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, news_id_for_args, form_data):
    """Авторизованный пользователь может создать комментарий."""
    # Arrange
    url = reverse('news:detail', args=news_id_for_args)

    # Act
    author_client.post(url, data=form_data)

    # Assert
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_id_for_args):
    """Комментарии с запрещенными словами не принимаются."""
    # Arrange
    url = reverse('news:detail', args=news_id_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

    # Act
    response = author_client.post(url, data=bad_words_data)

    # Assert
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, comment_id_for_args, news_id_for_args
):
    """Автор может удалить свой комментарий."""
    # Arrange
    delete_url = reverse('news:delete', args=comment_id_for_args)

    # Act
    response = author_client.post(delete_url)

    # Assert
    expected_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_id_for_args, news_id_for_args
):
    """Пользователь не может удалить комментарий другого автора."""
    # Arrange
    delete_url = reverse('news:delete', args=comment_id_for_args)

    # Act
    response = not_author_client.post(delete_url)

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, form_data, news_id_for_args
):
    """Автор может редактировать свои комментарии."""
    # Arrange
    edit_url = reverse('news:edit', args=(comment.id,))

    # Act
    response = author_client.post(edit_url, data=form_data)

    # Assert
    expected_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment_id_for_args, news_id_for_args, form_data
):
    """Пользователь не может редактировать чужие комментарии."""
    # Arrange
    edit_url = reverse('news:edit', args=comment_id_for_args)

    # Act
    response = not_author_client.post(edit_url, data=form_data)

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
