from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
User = get_user_model()


class TestNoteCreation(TestCase):
    """Тестирование создания заметки."""

    NOTE_TITLE = 'Заметка'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Создаем и регистрируем пользователя,
        подготавливаем данные для заметки.
        """
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_auth_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))


class TestNoteEditingDeletion(TestCase):
    """Тестирование редактирования и удаления заметки."""

    NOTE_TITLE = 'Заметка'
    NEW_NOTE_TITLE = 'Заметище'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Текст заметищи'

    @classmethod
    def setUpTestData(cls):
        """Создаем заметку, пользователей, адреса и данные для тестов."""
        cls.author = User.objects.create(username='автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.user = User.objects.create(username='авторизованный пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_author_can_edit_note(self):
        """Авторизованный пользователь может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        self.note.refresh_from_db()
        self.assertEqual(
            {self.note.title, self.note.text},
            {self.NEW_NOTE_TITLE, self.NEW_NOTE_TEXT}
        )

    def test_author_can_delete_note(self):
        """Авторизованный пользователь может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.note.refresh_from_db()
        self.assertEqual(
            {self.note.title, self.note.text},
            {self.NOTE_TITLE, self.NOTE_TEXT}
        )

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
