from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotes(TestCase):
    """Тестирование создания, редактирования и удаления заметок."""

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Проверка, что автор может создать заметку."""
        # Arrange
        self.client.force_login(self.author)
        url = reverse('notes:add')

        # Act
        response = self.client.post(url, data=self.form_data)

        # Assert
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        # Arrange
        url = reverse('notes:add')

        # Act
        response = self.client.post(url, data=self.form_data)

        # Assert
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        """Проверка, что нельзя создать заметку с неуникальным slug."""
        # Arrange
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug

        # Act
        response = self.client.post(url, data=self.form_data)
        form = response.context['form']

        # Assert
        self.assertTrue(form.has_error('slug'))
        self.assertEqual(form.errors['slug'][0], self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Проверка, что если slug пуст, он генерируется автоматически."""
        # Arrange
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data.pop('slug')

        # Act
        response = self.client.post(url, data=self.form_data)

        # Assert
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(title=self.form_data['title'])
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверка, что автор может редактировать свою заметку."""
        # Arrange
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))

        # Act
        response = self.client.post(url, self.form_data)

        # Assert
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Проверка, что другой пользователь не может редактировать заметку."""
        # Arrange
        self.client.force_login(self.not_author)
        url = reverse('notes:edit', args=(self.note.slug,))

        # Act
        response = self.client.post(url, self.form_data)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)

    def test_author_can_delete_note(self):
        """Проверка, что автор может удалить свою заметку."""
        # Arrange
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))

        # Act
        response = self.client.post(url)

        # Assert
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Проверка, что другой пользователь не может удалить заметку."""
        # Arrange
        self.client.force_login(self.not_author)
        url = reverse('notes:delete', args=(self.note.slug,))

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
