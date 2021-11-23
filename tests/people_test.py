import random
from json import dumps, loads
from uuid import uuid4

import pytest
import requests
from assertpy.assertpy import assert_that
from jsonpath_ng import parse

from utils.config import BASE_URI
from utils.print_helpers import pretty_print
from utils.file_reader import read_file


def test_read_all_has_kent():
    peoples, response = get_all_users()
    # Se verifica que la url responda con un status code 200
    assert_that(response.status_code).is_equal_to(requests.codes.ok)
    # Se almacenan los primeros nombres en una lista
    first_names = [people['fname'] for people in peoples]
    # Se comprueba que en la lista existe un usuario con nombre Kent
    assert_that(first_names).contains('Kent')


def test_add_new_user():
    unique_last_name = create_new_user_with_unique_last_name()

    peoples = requests.get(BASE_URI).json()
    new_user_created = search_users_by_last_name(peoples, unique_last_name)
    assert_that(new_user_created).is_not_empty()


def search_users_by_last_name(peoples, unique_last_name):
    return [person for person in peoples if person['lname'] == unique_last_name]


def test_delete_person():
    new_user_lastname = create_new_user_with_unique_last_name()
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


@pytest.fixture
def create_data():
    payload = read_file('create_person.json')

    random_no = random.randint(0,1000)
    last_name = f'Ardila{random_no}'

    payload['lname'] = last_name
    yield payload


def test_person_can_be_added_with_a_json_template(create_data):
    create_new_user_with_unique_last_name(create_data)

    response = requests.get(BASE_URI)
    peoples = loads(response.text)

    jsonpath_expr = parse("$.[*].lname")
    result = [match.value for match in jsonpath_expr.find(peoples)]

    expected_last_name = create_data['lname']
    assert_that(result).contains(expected_last_name)


def create_new_user_with_unique_last_name(body=None):
    if body is None:
        unique_last_name = f'User {str(uuid4())}'
        payload = dumps({
            'fname': 'New',
            'lname': unique_last_name
        })
    else:
        unique_last_name = body['lname']
        payload = dumps(body)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    request = requests.post(url=BASE_URI, data=payload, headers=headers)
    assert_that(request.status_code).is_equal_to(204)
    return unique_last_name
