from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):
    """Тестирование отображения страниц и доступности форм для заметок."""

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

    def test_notes_list_for_different_users(self):
        """Проверка доступности списка заметок для разных пользователей."""
        users_note_in_list = (
            (self.author, True),
            (self.not_author, False),
        )

        for user, note_in_list in users_note_in_list:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """Проверка наличия формы на страницах создания и редактирования заметок."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
