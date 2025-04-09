from http import HTTPStatus

from django.urls import reverse
import pytest

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',  # Имя параметра
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
# В фикстурах указывается встроенный клиент и имя параметра
def test_pages_avilability_for_anonymous_user(client, name):
    """Главная, логин, логаут и регистрация доступны всем пользователям."""
    # Адрес страницы получаем через reverse():
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_avilability_for_auth_user(not_author_client, name):
    """Страницы списка заметок, их создания и удаления доступны
    авторизованному пользователю.
    """
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


# Исрользуем два декоратора, чтобы протестировать для
# авторизованного и неавторизованного пользователя.
@pytest.mark.parametrize(
    # parametrized_client - название параметра, 
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'parametrized_client, expected_status',
    # В кортеже с кортежами передаём значения для параметров:
    (   
        
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND), 
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_users(
    parametrized_client, expected_status, name, note
):
    """Автор имеет доступ к страницам просмотра, редактирования и
    удаления своей заметки, а другой пользователь нет.
    """
    url = reverse(name, args=(note.slug,))
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, note_object',
    (
        ('notes:detail', pytest.lazy_fixture('note')),
        ('notes:edit', pytest.lazy_fixture('note')),
        ('notes:delete', pytest.lazy_fixture('note')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None)
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
def test_redirects(client, name, note_object):
    """Проверка редиректов для анонимного пользователя."""
    login_url = reverse('users:login')
    # Формируем URL в зависимости от того, передан ли объект заметки:
    if note_object is not None:
        url = reverse(name, args=(note_object.slug,))
    else:
        url = reverse(name)

    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
