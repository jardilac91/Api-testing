from json import dumps
from uuid import uuid4
from assertpy.assertpy import assert_that
from utils.config import BASE_URI
from utils.print_helpers import pretty_print
import requests


def test_read_all_has_kent():
    peoples, response = get_all_users()
    #Se verifica que la url responda con un status code 200
    assert_that(response.status_code).is_equal_to(requests.codes.ok)
    #Se almacenan los primeros nombres en una lista
    first_names = [people['fname'] for people in peoples]
    #Se comprueba que en la lista existe un usuario con nombre Kent
    assert_that(first_names).contains('Kent')


def test_add_new_user():
    unique_last_name = create_new_user()

    peoples = requests.get(BASE_URI).json()
    new_user_created = search_users_by_last_name(peoples, unique_last_name)
    assert_that(new_user_created).is_not_empty()


def search_users_by_last_name(peoples, unique_last_name):
    return [person for person in peoples if person['lname'] == unique_last_name]


def test_delete_person():
    new_user_lastname = create_new_user()
    all_users, _ = get_all_users()
    new_user = search_users_by_last_name(all_users, new_user_lastname)[0]

    pretty_print(new_user)
    person_to_be_deleted = new_user['person_id']

    url = f'{BASE_URI}/{person_to_be_deleted}'
    print(url)
    request = requests.delete(url)
    assert_that(request.status_code).is_equal_to(200)


def get_all_users():
    # Se obtiene la url
    response = requests.get(BASE_URI)
    # Se almacena la respuesta json en la variable
    peoples = response.json()
    return peoples, response


def create_new_user():
    unique_last_name = f'User {str(uuid4())}'
    payload = dumps({
        'fname': 'New',
        'lname': unique_last_name
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    request = requests.post(url=BASE_URI, data=payload, headers=headers)
    assert_that(request.status_code).is_equal_to(204)
    return unique_last_name