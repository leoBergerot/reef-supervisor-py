from decimal import Decimal
import random

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from .core.security import hash_password
from .db.session import engine
from .fixtures.fixtures import confirm_and_load_fixtures
from .main import app
from .managers import UserManager
from .repositories import ParameterRepository, PreferenceRepository, UserRepository
from .schemas import User

client = TestClient(app)


def test_read_main():
    # load fixtures
    with Session(engine) as session:
        confirm_and_load_fixtures(session)

    # test main page
    response = client.get("/")
    assert response.status_code == 404


def test_user_creation():
    # create user
    email = "leo.bergerot@reefsupervisor.fr"
    response = client.post("/users", json={
        "email": email,
        "password": "test",
    })

    assert response.status_code == 200
    assert response.json()['email'] == email

    parameter_repository = ParameterRepository()
    preference_repository = PreferenceRepository()
    user_repository = UserRepository()

    # check if preference it assigned to user
    user = user_repository.get_by_email(email)
    parameters = parameter_repository.get_all()
    preferences = preference_repository.get_by_user(user)
    assert len(parameters) == len(preferences)

    # test user already register
    response = client.post("/users", json={
        "email": email,
        "password": "test",
    })
    assert response.status_code == 400
    assert response.json()['detail'] == "Email already registered"

    # test email field validation
    response = client.post("/users", json={
        "email": "leobergerot",
        "password": "test",
    })
    assert response.status_code == 422


def test_create_user_admin():
    user_dict = {
        "email": "admin@reefsupervisor.fr",
        "password": hash_password("test"),
        "scopes": ["USER", "ADMIN"]
    }
    user = User(**user_dict)
    (UserManager(ParameterRepository())).create_add_preferences_persist(user)


@pytest.fixture(scope="session")
def auth_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "leo.bergerot@reefsupervisor.fr",
        "password": "test",
    }
    response = client.post("/token", headers=headers, data=data)
    assert response.status_code == 200
    return response.json()['access_token']


@pytest.fixture(scope="session")
def auth_token_admin():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "admin@reefsupervisor.fr",
        "password": "test",
    }
    response = client.post("/token", headers=headers, data=data)
    assert response.status_code == 200
    return response.json()['access_token']


def test_preferences(auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = client.get("/preferences", headers=headers)
    assert response.status_code == 200

    preference_id = response.json()[0]['id']

    # update preferences
    response = client.patch(f"/preferences/{preference_id}", headers=headers, json={"enabled": False})
    assert response.status_code == 200
    assert response.json()["enabled"] == False


def test_tanks(auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    tank_name = "First tank"
    response = client.post("/tanks", headers=headers, json={"name": tank_name})
    assert response.status_code == 200
    assert response.json()["name"] == tank_name

    response = client.get("/tanks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    return response.json()


def test_update_parameter(auth_token_admin):
    headers = {
        "Authorization": f"Bearer {auth_token_admin}"
    }

    response = client.get("/parameters", headers=headers)
    assert response.status_code == 200
    parameter = response.json()[0]
    id = parameter.pop('id', None)
    parameter['need_value'] = False
    response = client.put(f"/parameters/{id}", headers=headers, json=parameter)

    assert response.json()['need_value'] == False


def test_create_measure(auth_token, auth_token_admin):
    test_no_value_validation = False
    test_value_validation = False
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    response = client.get("/tanks", headers=headers)
    tank = response.json()[0]

    response = client.get("/parameters", headers=headers)
    assert response.status_code == 200
    parameters = response.json()
    for parameter in parameters:
        measure = {
            "tank_id": tank['id'],
            "parameter_id": parameter['id'],
        }
        value = random.randint(1, 100)
        if parameter['need_value']:
            measure['value'] = value
        response = client.post("measures", headers=headers, json=measure)
        assert response.status_code == 200
        measure_response = response.json()
        if parameter['need_value']:
            assert Decimal(measure_response['value']) == value
        else:
            assert measure_response['value'] is None

        if parameter['need_value'] and not test_value_validation:
            test_value_validation = True
            measure.pop('value')
            response = client.post("measures", headers=headers, json=measure)
            assert response.status_code == 422

        if not parameter['need_value'] and not test_no_value_validation:
            test_no_value_validation = True
            measure['value'] = 10
            response = client.post("measures", headers=headers, json=measure)
            assert response.status_code == 422

        assert isinstance(measure_response['id'], int)

    headers = {
        "Authorization": f"Bearer {auth_token_admin}"
    }

    measure = {
        "tank_id": tank['id'],
        "parameter_id": parameters[0]['id'],
    }
    if parameters[0]['need_value']:
        measure['value'] = 10

    response = client.post("measures", headers=headers, json=measure)
    assert response.status_code == 401
