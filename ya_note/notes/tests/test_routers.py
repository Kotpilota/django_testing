from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование доступности страниц для разных пользователей."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous_user(self):
        """Проверка доступности страниц для анонимных пользователей."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)

                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверка доступности страниц для авторизованных пользователей."""
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        self.client.force_login(self.author)

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)

                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Проверка доступности страниц для разных пользователей."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))

                    response = self.client.get(url)

                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа для анонимных пользователей."""
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'

                response = self.client.get(url)

                self.assertRedirects(response, redirect_url)
