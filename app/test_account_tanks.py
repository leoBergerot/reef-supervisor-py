from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core import rate_limit as rate_limit_module
from app.db.session import engine
from app.fixtures.fixtures import load_fixtures
from app.main import app
from app.schemas import Parameter, User

client = TestClient(app)


def _email() -> str:
    return f"user-{uuid4().hex}@reefsupervisor.fr"


def _auth(email: str, password: str = "test") -> str:
    response = client.post("/token", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _activate(email: str) -> None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).one()
        user.is_active = True
        session.add(user)
        session.commit()


def _create_user(email: str, password: str = "test", *, activate: bool = True) -> dict:
    response = client.post("/users", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    if activate:
        _activate(email)
    return response.json()


def _ensure_parameters() -> None:
    with Session(engine) as session:
        if session.exec(select(Parameter)).first() is None:
            load_fixtures(session)


def _set_need_value(parameter_id: int, need_value: bool) -> None:
    with Session(engine) as session:
        parameter = session.get(Parameter, parameter_id)
        parameter.need_value = need_value
        session.add(parameter)
        session.commit()


def test_account_activation_and_password_reset(capture_auth_emails):
    email = _email()
    created = _create_user(email, activate=False)
    assert "token" not in created
    assert client.post("/token", data={"username": email, "password": "test"}).status_code == 401

    assert len(capture_auth_emails["activation"]) == 1
    assert capture_auth_emails["activation"][0]["email"] == email
    activation = capture_auth_emails["activation"][0]["token"]

    assert client.post("/account-activations/confirm", json={"token": "not-a-token"}).status_code == 400
    confirmed = client.post("/account-activations/confirm", json={"token": activation})
    assert confirmed.status_code == 200
    assert confirmed.json()["email"] == email
    assert _auth(email)

    capture_auth_emails["activation"].clear()
    capture_auth_emails["reset"].clear()

    missing = client.post("/forgot-password", json={"email": "missing@reefsupervisor.fr"})
    assert missing.status_code == 200
    assert "token" not in missing.json()
    assert missing.json()["detail"]
    assert capture_auth_emails["reset"] == []

    reset = client.post("/forgot-password", json={"email": email})
    assert reset.status_code == 200
    assert "token" not in reset.json()
    assert reset.json()["detail"] == missing.json()["detail"]
    assert len(capture_auth_emails["reset"]) == 1
    reset_payload = capture_auth_emails["reset"][0]
    assert reset_payload["email"] == email
    user_id = reset_payload["user_id"]
    token = reset_payload["token"]

    rate_limit_module.auth_rate_limiter.reset()
    assert client.post("/recover-password", json={
        "id": user_id,
        "token": "not-a-token",
        "password": "replaced",
    }).status_code == 400
    assert client.post("/recover-password", json={
        "id": user_id + 9999,
        "token": token,
        "password": "replaced",
    }).status_code == 400

    changed = client.post("/recover-password", json={
        "id": str(user_id),
        "token": token,
        "password": "replaced",
    })
    assert changed.status_code == 200
    assert changed.json()["id"] == user_id
    assert client.post("/token", data={"username": email, "password": "test"}).status_code == 401
    assert _auth(email, "replaced")
    assert client.post("/recover-password", json={
        "id": user_id,
        "token": token,
        "password": "again",
    }).status_code == 400


def test_tank_update_photo_and_delete():
    email = _email()
    other = _email()
    _create_user(email)
    _create_user(other)
    headers = {"Authorization": f"Bearer {_auth(email)}"}
    other_headers = {"Authorization": f"Bearer {_auth(other)}"}

    created = client.post("/tanks", headers=headers, json={"name": "Reef", "water_type": "seawater"})
    assert created.status_code == 200
    tank_id = created.json()["id"]
    assert created.json()["photo_url"] is None
    assert created.json()["water_type"] == "seawater"

    renamed = client.patch(f"/tanks/{tank_id}", headers=headers, json={"name": "Lagoon"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Lagoon"
    assert renamed.json()["water_type"] == "seawater"
    assert client.patch(f"/tanks/{tank_id}", headers=other_headers, json={"name": "Stolen"}).status_code == 404
    assert client.patch(f"/tanks/{tank_id}", headers=headers, json={"name": ""}).status_code == 422

    uploaded = client.patch(
        f"/tanks/{tank_id}/photo",
        headers=headers,
        files={"file": ("tank.svg", b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", "image/svg+xml")},
    )
    assert uploaded.status_code == 200
    assert uploaded.json()["photo_url"] == f"/tanks/{tank_id}/photo"
    photo = client.get(f"/tanks/{tank_id}/photo", headers=headers)
    assert photo.status_code == 200
    assert photo.headers["content-type"].startswith("image/svg+xml")
    assert b"<svg" in photo.content
    assert client.get(f"/tanks/{tank_id}/photo", headers=other_headers).status_code == 404
    rejected = client.patch(
        f"/tanks/{tank_id}/photo",
        headers=headers,
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert rejected.status_code == 400

    listed = client.get("/tanks", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Lagoon"
    assert listed.json()[0]["photo_url"] == f"/tanks/{tank_id}/photo"

    assert client.delete(f"/tanks/{tank_id}", headers=other_headers).status_code == 404
    deleted = client.delete(f"/tanks/{tank_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get("/tanks", headers=headers).json() == []
    assert client.get(f"/tanks/{tank_id}/photo", headers=headers).status_code == 404


def test_set_measure_timestamp_without_value():
    _ensure_parameters()
    email = _email()
    _create_user(email)
    headers = {"Authorization": f"Bearer {_auth(email)}"}
    tank_id = client.post("/tanks", headers=headers, json={"name": "Bare", "water_type": "freshwater"}).json()["id"]
    tank_params = client.get(f"/tanks/{tank_id}/parameters", headers=headers).json()
    assert tank_params
    bare = next(item["parameter"] for item in tank_params if item["parameter"]["name"] == "Water change")
    valued = next(item["parameter"] for item in tank_params if item["parameter"]["name"] == "Temperature")
    previous_bare = bare["need_value"]
    previous_valued = valued["need_value"]
    _set_need_value(bare["id"], False)
    _set_need_value(valued["id"], True)
    try:
        created = client.post("/measures", headers=headers, json={"tank_id": tank_id, "parameter_id": bare["id"]})
        assert created.status_code == 200, created.text
        assert created.json()["value"] is None
        stamp = datetime(2024, 5, 1, 8, 30, tzinfo=UTC).isoformat().replace("+00:00", "Z")
        updated = client.patch(
            f"/measures/{created.json()['id']}/timestamp",
            headers=headers,
            json={"created_at": stamp},
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["value"] is None
        stored = datetime.fromisoformat(updated.json()["created_at"])
        assert stored.replace(tzinfo=None) == datetime(2024, 5, 1, 8, 30)

        valued_measure = client.post("/measures", headers=headers, json={
            "tank_id": tank_id,
            "parameter_id": valued["id"],
            "value": 12,
        })
        assert valued_measure.status_code == 200, valued_measure.text
        rejected = client.patch(
            f"/measures/{valued_measure.json()['id']}/timestamp",
            headers=headers,
            json={"created_at": stamp},
        )
        assert rejected.status_code == 422

        assert client.delete(f"/tanks/{tank_id}", headers=headers).status_code == 204
        remaining = client.get("/measures", headers=headers)
        assert remaining.status_code == 200
        assert remaining.json()["total"] == 0
    finally:
        _set_need_value(bare["id"], previous_bare)
        _set_need_value(valued["id"], previous_valued)
