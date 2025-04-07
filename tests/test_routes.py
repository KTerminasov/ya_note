from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from notes.models import Note

from django.contrib.auth import get_user_model
User = get_user_model()


class TestRoutes(TestCase):
    """Класс для тестирования url-адресов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Создатель заметки')
        cls.note = Note.objects.create(
            title='Название',
            text='Текст',
            author=cls.author
        )

        cls.another_user = User.objects.create(username='Другой пользователь')

    def test_pages_availability(self):
        """Тестирование доступности страниц анонимным пользователям."""
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_aviability_for_add_and_view_list_of_notes(self):
        """Проверка доступа к добавлению заметки и просмотра всех заметок."""
        self.client.force_login(self.another_user)

        for name in ('notes:add', 'notes:list'):
            with self.subTest(name=name, user=self.another_user):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_aviability_for_note_edit_view_and_delete(self):
        """Проверка доступа к редактированию, просмотру и удалению заметок."""
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_user, HTTPStatus.NOT_FOUND)
        )

        note_slug = self.note.slug
        urls = (
            (('notes:edit'), (note_slug,)),
            (('notes:detail'), (note_slug,)),
            (('notes:delete'), (note_slug,)),
        )

        for user, status in user_statuses:
            self.client.force_login(user)

            for name, args in urls:
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_users(self):
        """Проверка переадресации анонимных пользователей."""
        login_url = reverse('users:login')

        note_slug = self.note.slug
        urls = (
            (('notes:add'), None),
            (('notes:list'), None),
            (('notes:edit'), (note_slug,)),
            (('notes:detail'), (note_slug,)),
            (('notes:delete'), (note_slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
