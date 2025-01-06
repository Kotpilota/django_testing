from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news_id_for_args):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, news_id_for_args, form_data):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    author_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_id_for_args):
    """Комментарии с запрещенными словами не принимаются."""
    url = reverse('news:detail', args=news_id_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client, comment_id_for_args, news_id_for_args
):
    """Автор может удалить свой комментарий."""
    delete_url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(delete_url)
    expected_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_id_for_args, news_id_for_args
):
    """Пользователь не может удалить комментарий другого автора."""
    delete_url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, form_data, news_id_for_args
):
    """Автор может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    expected_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment_id_for_args, news_id_for_args, form_data
):
    """Пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
