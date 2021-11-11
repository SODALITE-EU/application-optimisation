import json
import pathlib

from fastapi.testclient import TestClient

from MODAK.app import app
from MODAK.model import Script, ScriptIn

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200


def test_optimise():
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    assert "job_script" not in req_content["job"]
    assert "build_script" not in req_content["job"]
    response = client.post("/optimise", json=req_content)
    assert response.status_code == 200
    assert response.json()["job"]["job_script"]
    assert response.json()["job"]["build_script"]


def test_get_image():
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    assert "container_runtime" not in req_content["job"]["application"]
    response = client.post("/get_image", json=req_content)
    assert response.status_code == 200
    assert "container_runtime" in response.json()["job"]["application"]


def test_get_build():
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    assert "build_script" not in req_content["job"]
    response = client.post("/get_build", json=req_content)
    assert response.status_code == 200
    assert response.json()["job"]["build_script"]


def test_get_optimise():
    req_content = json.loads(SCRIPT_DIR.joinpath("input/mpi_test.json").read_text())
    response = client.post("/get_optimisation", json=req_content)
    assert response.status_code == 200
    assert response.json()["job"]["job_content"]


def test_create_and_get_script_roundtrip():
    desc = "test"
    script = ScriptIn(description=desc, conditions={}, data={"stage": "pre"})

    response = client.post("/scripts", json=script.dict())
    assert response.status_code == 201

    script_list = Script.parse_obj(response.json())

    assert script_list
    assert script_list.description == desc

    response = client.get(f"/scripts/{script_list.id}")
    print(f"/scripts/{script_list.id}", response)
    assert response.status_code == 200
    script = Script.parse_obj(response.json())

    assert script.id == script_list.id
    assert script.description == desc
