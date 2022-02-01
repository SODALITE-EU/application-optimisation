import json
import pathlib
from unittest.mock import patch

import pytest
from sqlalchemy import delete, insert, select

from MODAK.db import Map, Optimisation
from MODAK.driver import Driver
from MODAK.mapper import Mapper
from MODAK.model import JobModel
from MODAK.settings import Settings

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


@pytest.fixture
def driver_mapper():
    """Create a driver and mapper with the test DB"""
    driver = Driver()
    mapper = Mapper(driver)
    yield driver, mapper


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_add_opt(driver_mapper):
    driver, mapper = driver_mapper

    target_string = '{"cpu_type":"x86","acc_type":"nvidia"}'
    opt_string = '{"xla":true,"version":"1.1"}'

    stmt = delete(Optimisation).where(
        Optimisation.opt_dsl_code == "TF_PIP_XLA"
    )  # no need to delete Mapper, since DB is set to CASCADE
    await driver.update_sql(stmt)
    await mapper.add_optimisation(
        "TF_PIP_XLA",
        "tensorflow",
        json.loads(target_string),
        json.loads(opt_string),
    )
    data = await driver.select_sql(
        select(Optimisation.app_name).where(Optimisation.opt_dsl_code == "TF_PIP_XLA")
    )
    assert len(data) == 1
    assert data[0][0] == "tensorflow"


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_add_container(driver_mapper):
    driver, mapper = driver_mapper

    stmt = delete(Map).where(Map.opt_dsl_code == "TF_PIP_XLA")
    await driver.update_sql(stmt)
    data = await driver.select_sql(
        select(Map.container_file).where(Map.opt_dsl_code == "TF_PIP_XLA")
    )
    assert len(data) == 0
    await mapper.add_container(
        "TF_PIP_XLA", "AI/containers/tensorflow/tensorflow_pip_xla"
    )
    data = await driver.select_sql(
        select(Map.container_file).where(Map.opt_dsl_code == "TF_PIP_XLA")
    )
    assert len(data) == 1
    assert data[0][0] == "AI/containers/tensorflow/tensorflow_pip_xla"


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_map_container_ai(driver_mapper):
    driver, mapper = driver_mapper

    dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"

    model = JobModel.parse_raw(dsl_file.read_text())
    new_container = await mapper.map_container(
        model.job.application, model.job.optimisation
    )
    assert new_container == "docker.io://modakopt/modak:tensorflow-2.1-gpu-src"


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_map_container_hpc(driver_mapper):
    driver, mapper = driver_mapper

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    assert model.job.optimisation

    dsl_code = await mapper._decode_hpc_opt(
        model.job.application.app_tag, model.job.optimisation
    )
    assert dsl_code == "mpich_ub1804_cuda101_mpi314_gnugprof"


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_map_container_aliased(driver_mapper):
    _, mapper = driver_mapper

    dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"

    with patch.object(Settings, "image_hub_aliases", {"docker": "docker.invalid"}):
        model = JobModel.parse_raw(dsl_file.read_text())
        new_container = await mapper.map_container(
            model.job.application, model.job.optimisation
        )
        assert new_container == "docker.invalid://modakopt/modak:tensorflow-2.1-gpu-src"


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_non_app_tag_mapping(driver):
    mapper = Mapper(driver)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich",
        app_name="mpich",
        target="enable_opt_build:true,cpu_type:x86,acc_type:nvidia,",
        optimisation="version:3.1.4|",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich",
        container_file="nvidia_mpich",
        image_type="shub",
        image_hub="library",
    )
    await driver.update_sql(optstmt)
    await driver.update_sql(mapstmt)

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    assert await mapper._decode_hpc_opt(
        model.job.application.app_tag, model.job.optimisation
    )
    assert await mapper.map_container(model.job.application, model.job.optimisation)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_app_tag_mapping_missing(driver):
    mapper = Mapper(driver)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich",
        app_name="mpich",
        target="enable_opt_build:true,cpu_type:x86,acc_type:nvidia,",
        optimisation="version:3.1.4|",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich",
        container_file="nvidia_mpich",
        image_type="shub",
        image_hub="library",
    )
    await driver.update_sql(optstmt)
    await driver.update_sql(mapstmt)

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    model.job.application.app_tag = "code_aster"

    assert not await mapper._decode_hpc_opt(
        model.job.application.app_tag, model.job.optimisation
    )
    assert not await mapper.map_container(model.job.application, model.job.optimisation)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_app_tag_mapping(driver):
    mapper = Mapper(driver)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich",
        app_name="mpich",
        target="enable_opt_build:true,cpu_type:x86,acc_type:nvidia,",
        optimisation="version:3.1.4|",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich",
        container_file="nvidia_mpich",
        image_type="shub",
        image_hub="library",
    )
    await driver.update_sql(optstmt)
    await driver.update_sql(mapstmt)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich-code_aster",
        app_name="code_aster",
        target="enable_opt_build:false,cpu_type:x86,acc_type:nvidia",
        optimisation="version:3.1.4|library:mpich",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich-code_aster",
        container_file="nvidia_mpich-code_aster_avx2",
        image_type="shub",
        image_hub="library",
    )
    await driver.update_sql(optstmt)
    await driver.update_sql(mapstmt)

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    model.job.application.app_tag = "code_aster"
    model.job.optimisation.enable_opt_build = (
        False  # there is not much in requesting an optimization build now
    )

    dsl_code = await mapper._decode_hpc_opt(
        model.job.application.app_tag, model.job.optimisation
    )
    assert dsl_code
    assert dsl_code == "nvidia-mpich-code_aster"
    assert await mapper.map_container(model.job.application, model.job.optimisation)
