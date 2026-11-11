from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db.session import engine
from app.fixtures.fixtures import load_fixtures
from app.main import app
from app.schemas import Parameter

client = TestClient(app)

SEAWATER_DEFAULTS = {
    "Temperature",
    "Alkalinity",
    "Calcium",
    "Magnesium",
    "Nitrate",
    "Phosphate",
    "Salinity",
}
FRESHWATER_DEFAULTS = {
    "Temperature",
    "Power of hydrogen",
    "Alkalinity",
    "Nitrite",
    "Nitrate",
    "Water change",
}


def _email() -> str:
    return f"user-{uuid4().hex}@reefsupervisor.fr"


def _auth(email: str, password: str = "test") -> str:
    response = client.post("/token", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _create_user(email: str, password: str = "test") -> dict:
    response = client.post("/users", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def _ensure_parameters() -> None:
    with Session(engine) as session:
        if session.exec(select(Parameter).where(Parameter.is_custom == False)).first() is None:  # noqa: E712
            load_fixtures(session)


def _headers() -> dict:
    _ensure_parameters()
    email = _email()
    _create_user(email)
    return {"Authorization": f"Bearer {_auth(email)}"}


def test_alkalinity_catalog_is_numeric():
    headers = _headers()
    catalog = client.get("/parameters", headers=headers).json()
    alkalinity = next(item for item in catalog if item["name"] == "Alkalinity")
    assert alkalinity["sub_name"] == "KH"
    assert alkalinity["need_value"] is True


def test_create_tank_requires_water_type():
    headers = _headers()
    response = client.post("/tanks", headers=headers, json={"name": "No type"})
    assert response.status_code == 422


def test_seawater_and_freshwater_default_seeds():
    headers = _headers()

    seawater = client.post("/tanks", headers=headers, json={"name": "Reef", "water_type": "seawater"})
    assert seawater.status_code == 200, seawater.text
    seawater_params = client.get(f"/tanks/{seawater.json()['id']}/parameters", headers=headers)
    assert seawater_params.status_code == 200
    seawater_names = {item["parameter"]["name"] for item in seawater_params.json()}
    assert seawater_names == SEAWATER_DEFAULTS
    assert all(item["enabled"] for item in seawater_params.json())
    assert all(not item["is_custom"] for item in seawater_params.json())

    freshwater = client.post("/tanks", headers=headers, json={"name": "Community", "water_type": "freshwater"})
    assert freshwater.status_code == 200, freshwater.text
    freshwater_params = client.get(f"/tanks/{freshwater.json()['id']}/parameters", headers=headers)
    assert freshwater_params.status_code == 200
    freshwater_names = {item["parameter"]["name"] for item in freshwater_params.json()}
    assert freshwater_names == FRESHWATER_DEFAULTS


def test_create_with_enabled_parameter_ids_and_customs():
    headers = _headers()
    catalog = client.get("/parameters", headers=headers).json()
    by_name = {item["name"]: item["id"] for item in catalog}
    enabled_ids = [by_name["Temperature"], by_name["Alkalinity"]]

    created = client.post(
        "/tanks",
        headers=headers,
        json={
            "name": "Custom mix",
            "water_type": "seawater",
            "enabled_parameter_ids": enabled_ids,
            "custom_parameters": [{"name": "Iron", "unit": "Fe"}],
        },
    )
    assert created.status_code == 200, created.text
    tank_id = created.json()["id"]

    params = client.get(f"/tanks/{tank_id}/parameters", headers=headers).json()
    names = {item["parameter"]["name"] for item in params}
    assert names == {"Temperature", "Alkalinity", "Iron"}
    iron = next(item for item in params if item["parameter"]["name"] == "Iron")
    assert iron["is_custom"] is True
    assert iron["enabled"] is True
    assert iron["parameter"]["sub_name"] == "Fe"
    assert iron["parameter"]["need_value"] is True

    catalog_names = {item["name"] for item in client.get("/parameters", headers=headers).json()}
    assert "Iron" not in catalog_names


def test_unknown_enabled_parameter_ids_are_rejected():
    headers = _headers()
    response = client.post(
        "/tanks",
        headers=headers,
        json={"name": "Bad", "water_type": "seawater", "enabled_parameter_ids": [999999]},
    )
    assert response.status_code == 422


def test_patch_toggle_and_measure_gate():
    headers = _headers()
    other = _email()
    _create_user(other)
    other_headers = {"Authorization": f"Bearer {_auth(other)}"}

    created = client.post("/tanks", headers=headers, json={"name": "Reef", "water_type": "seawater"})
    tank_id = created.json()["id"]
    params = client.get(f"/tanks/{tank_id}/parameters", headers=headers).json()
    temperature = next(item for item in params if item["parameter"]["name"] == "Temperature")
    parameter_id = temperature["parameter"]["id"]

    assert client.get(f"/tanks/{tank_id}/parameters", headers=other_headers).status_code == 404

    disabled = client.patch(
        f"/tanks/{tank_id}/parameters",
        headers=headers,
        json={"parameters": [{"parameter_id": parameter_id, "enabled": False}]},
    )
    assert disabled.status_code == 200, disabled.text
    updated = next(item for item in disabled.json() if item["parameter"]["id"] == parameter_id)
    assert updated["enabled"] is False

    rejected = client.post(
        "/measures",
        headers=headers,
        json={"tank_id": tank_id, "parameter_id": parameter_id, "value": 25},
    )
    assert rejected.status_code == 422

    enabled = client.patch(
        f"/tanks/{tank_id}/parameters",
        headers=headers,
        json={"parameters": [{"parameter_id": parameter_id, "enabled": True}]},
    )
    assert enabled.status_code == 200
    accepted = client.post(
        "/measures",
        headers=headers,
        json={"tank_id": tank_id, "parameter_id": parameter_id, "value": 25},
    )
    assert accepted.status_code == 200, accepted.text


def test_post_custom_parameter_and_measure():
    headers = _headers()
    tank_id = client.post(
        "/tanks",
        headers=headers,
        json={"name": "Reef", "water_type": "seawater", "enabled_parameter_ids": []},
    ).json()["id"]

    custom = client.post(
        f"/tanks/{tank_id}/parameters/custom",
        headers=headers,
        json={"name": "Iodine", "unit": "I"},
    )
    assert custom.status_code == 200, custom.text
    assert custom.json()["is_custom"] is True
    parameter_id = custom.json()["parameter"]["id"]

    measure = client.post(
        "/measures",
        headers=headers,
        json={"tank_id": tank_id, "parameter_id": parameter_id, "value": 0.06},
    )
    assert measure.status_code == 200, measure.text

    disabled = client.patch(
        f"/tanks/{tank_id}/parameters",
        headers=headers,
        json={"parameters": [{"parameter_id": parameter_id, "enabled": False}]},
    )
    assert disabled.status_code == 200
    assert client.post(
        "/measures",
        headers=headers,
        json={"tank_id": tank_id, "parameter_id": parameter_id, "value": 0.07},
    ).status_code == 422


def test_enable_catalog_parameter_not_seeded():
    headers = _headers()
    catalog = {item["name"]: item["id"] for item in client.get("/parameters", headers=headers).json()}
    tank_id = client.post(
        "/tanks",
        headers=headers,
        json={
            "name": "Minimal",
            "water_type": "seawater",
            "enabled_parameter_ids": [catalog["Temperature"]],
        },
    ).json()["id"]

    magnesium_id = catalog["Magnesium"]
    patched = client.patch(
        f"/tanks/{tank_id}/parameters",
        headers=headers,
        json={"parameters": [{"parameter_id": magnesium_id, "enabled": True}]},
    )
    assert patched.status_code == 200, patched.text
    names = {item["parameter"]["name"] for item in patched.json()}
    assert "Magnesium" in names
    assert client.post(
        "/measures",
        headers=headers,
        json={"tank_id": tank_id, "parameter_id": magnesium_id, "value": 1300},
    ).status_code == 200


def test_reorder_tank_parameters_via_sort_order():
    headers = _headers()
    tank_id = client.post(
        "/tanks",
        headers=headers,
        json={"name": "Ordered", "water_type": "seawater"},
    ).json()["id"]
    params = client.get(f"/tanks/{tank_id}/parameters", headers=headers).json()
    assert len(params) >= 2
    assert all("sort_order" in item for item in params)
    first, second = params[0], params[1]
    reordered = client.patch(
        f"/tanks/{tank_id}/parameters",
        headers=headers,
        json={
            "parameters": [
                {
                    "parameter_id": first["parameter"]["id"],
                    "enabled": True,
                    "sort_order": 1,
                },
                {
                    "parameter_id": second["parameter"]["id"],
                    "enabled": True,
                    "sort_order": 0,
                },
            ]
        },
    )
    assert reordered.status_code == 200, reordered.text
    by_id = {item["parameter"]["id"]: item for item in reordered.json()}
    assert by_id[first["parameter"]["id"]]["sort_order"] == 1
    assert by_id[second["parameter"]["id"]]["sort_order"] == 0
    listed = client.get(f"/tanks/{tank_id}/parameters", headers=headers).json()
    enabled = [item for item in listed if item["enabled"]]
    assert enabled[0]["parameter"]["id"] == second["parameter"]["id"]
    assert enabled[1]["parameter"]["id"] == first["parameter"]["id"]
