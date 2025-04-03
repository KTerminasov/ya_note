from django.test import TestCase
from notes.models import Note
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()


class TestContent(TestCase):
    """Тестирование контента."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Создатель заметки')
        Note.objects.bulk_create(
            Note(
                title=f'Заметка №{i}',
                text='Текст',
                author=cls.author,
                slug=f'note-{i}'
            )
            for i in range(5)
        )
    
    def test_notes_order(self):
        """Проверка сортировки заметок по id."""
        self.client.force_login(self.author)

        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        
        all_notes = [note.id for note in object_list]
        sorted_notes = sorted(all_notes)

        self.assertEqual(all_notes, sorted_notes)
