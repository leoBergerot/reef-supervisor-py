import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from .db.session import engine
from .fixtures.fixtures import confirm_and_load_fixtures
from .main import app
from .repositories import ParameterRepository, PreferenceRepository, UserRepository

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
