import json
import pathlib
from typing import AsyncIterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from MODAK import db
from MODAK.app import app, authentication_token, get_db_session, get_driver
from MODAK.driver import Driver
from MODAK.model import Script, ScriptIn
from MODAK.model.infrastructure import InfrastructureIn
from MODAK.model.scaling import ApplicationScalingModelIn

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


engine = create_async_engine("sqlite+aiosqlite:///", future=True)
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def override_get_db_session() -> AsyncIterator[AsyncSession]:
    async with TestingSessionLocal() as session:
        yield session


def override_get_driver() -> Driver:
    return Driver(engine)


app.dependency_overrides[get_db_session] = override_get_db_session
app.dependency_overrides[get_driver] = override_get_driver


@app.on_event("startup")
async def startup_event():
    """Create the database structure in the empty test database"""
    async with engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_optimise(client):
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    assert "job_script" not in req_content["job"]
    assert "build_script" not in req_content["job"]
    response = client.post("/optimise", json=req_content)
    assert response.status_code == 200
    assert response.json()["job"]["job_script"]
    assert response.json()["job"]["build_script"]


def test_get_image(client):
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    assert "container_runtime" not in req_content["job"]["application"]
    response = client.post("/get_image", json=req_content)
    assert response.status_code == 200
    assert "container_runtime" in response.json()["job"]["application"]


def test_get_build(client):
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    assert "build_script" not in req_content["job"]
    response = client.post("/get_build", json=req_content)
    assert response.status_code == 200
    assert response.json()["job"]["build_script"]


def test_get_optimise(client):
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    response = client.post("/get_optimisation", json=req_content)
    assert response.status_code == 200
    assert response.json()["job"]["job_content"]


def test_create_infrastructure_example(client):
    """Test that the infrastructure example we give can be added, but not a 2nd time"""

    response = client.post(
        "/infrastructures",
        json=InfrastructureIn.schema()["example"],
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 201

    response = client.post(
        "/infrastructures",
        json=InfrastructureIn.schema()["example"],
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 409


def test_create_script_example(client):
    """Test that the script example we give can be added. Relies on the previous test to run."""

    response = client.post(
        "/scripts",
        json=ScriptIn.schema()["example"],
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 201


def test_create_and_get_script_roundtrip(client):
    desc = "test"
    script = ScriptIn(description=desc, conditions={}, data={"stage": "pre"})

    response = client.post(
        "/scripts",
        json=script.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 201

    script_list = Script.parse_obj(response.json())

    assert script_list
    assert script_list.description == desc

    response = client.get(f"/scripts/{script_list.id}")
    assert response.status_code == 200
    script = Script.parse_obj(response.json())

    assert script.id == script_list.id
    assert script.description == desc


def test_create_script_invalid_conditions(client):
    script = ScriptIn(
        conditions={"infrastructure": {"name": "missing-infra"}}, data={"stage": "pre"}
    )
    response = client.post(
        "/scripts",
        json=script.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 409

    infra = InfrastructureIn(name="fictitious-infra", configuration={})
    response = client.post(
        "/infrastructures",
        json=infra.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    response.raise_for_status()

    script = ScriptIn(
        conditions={
            "infrastructure": {
                "name": "fictitious-infra",
                "storage_class": "default-foobar",
            }
        },
        data={"stage": "pre"},
    )
    response = client.post(
        "/scripts",
        json=script.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 409


def test_create_script_valid_storage(client):
    infra = InfrastructureIn(
        name="less-fictitious-infra",
        configuration={
            "storage": {
                "file:///scratch": {
                    "storage_class": "default-high",
                },
                "file:///data": {
                    "storage_class": "default-common",
                },
            },
        },
    )
    response = client.post(
        "/infrastructures",
        json=infra.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    response.raise_for_status()

    script = ScriptIn(
        conditions={
            "infrastructure": {
                "name": "less-fictitious-infra",
                "storage_class": "default-common",
            }
        },
        data={"stage": "pre"},
    )
    response = client.post(
        "/scripts",
        json=script.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 201


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_create_scaling_model(client):
    async with engine.begin() as conn:
        await conn.execute(
            insert(db.Optimisation).values(
                opt_dsl_code="test-code-01", app_name="test-app-01"
            )
        )

    smodel = ApplicationScalingModelIn(
        opt_dsl_code="test-code-01", model={"name": "noop"}
    )
    response = client.post(
        "/scaling_models",
        json=smodel.dict(),
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 201


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_create_scaling_model_example(client):
    """Verify that the model example can be added"""

    model_json = ApplicationScalingModelIn.schema()["example"]

    async with engine.begin() as conn:
        await conn.execute(
            insert(db.Optimisation).values(
                opt_dsl_code=model_json["opt_dsl_code"], app_name="test-app-01"
            )
        )

    response = client.post(
        "/scaling_models",
        json=model_json,
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    assert response.status_code == 201


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_create_mapping(client):
    opt_dsl_code = "modak-tensorflow-2.2.1-gpu-py3-TEST"
    mapping = {
        "opt_dsl_code": opt_dsl_code,
        "app_name": "tensorflow",
        "version": "2.2.1",
        "enable_opt_build": True,
        "target": {"cpu_type": "x86", "acc_type": "nvidia"},
        "selectors": {"xla": True, "version": "2.2.1"},
        "container_name": "tensorflow_2.2.1-gpu-py3",
        "container_type": "shub",
        "container_registry": "library",
    }

    response = client.post(
        "/container_mappings",
        json=mapping,
        headers={"Authorization": f"Bearer {authentication_token.api_key}"},
    )
    response.raise_for_status()
    resp_json = response.json()

    assert resp_json["opt_dsl_code"] == opt_dsl_code

    response = client.get(
        "/container_mappings",
    )
    response.raise_for_status()
    assert response.json()[0]["opt_dsl_code"] == opt_dsl_code

    response = client.get(
        f"/container_mappings/{opt_dsl_code}",
    )
    response.raise_for_status()
