import pytest
from pydantic import ValidationError
from sqlalchemy import insert

from MODAK import db
from MODAK.mapper import Mapper
from MODAK.model import Application
from MODAK.model.scaling import (
    ApplicationScalingModelIn,
    ScalingModelAmdahl,
    ScalingModelNoop,
)
from MODAK.scaler import Scaler


def test_dispatch():
    """Test that the pydantic dispatch based on the name works"""

    appmodel_amdahl = ApplicationScalingModelIn(
        opt_dsl_code="", model={"name": "amdahl", "F": 0.5}
    )
    assert isinstance(appmodel_amdahl.model, ScalingModelAmdahl)

    appmodel_noop = ApplicationScalingModelIn(opt_dsl_code="", model={"name": "noop"})
    assert isinstance(appmodel_noop.model, ScalingModelNoop)


def test_invalid_input():
    """Test that the pydantic parameter validation works"""

    with pytest.raises(ValidationError):
        ApplicationScalingModelIn(opt_dsl_code="", model={"name": "amdahl", "G": 0.5})

    with pytest.raises(ValidationError):
        ApplicationScalingModelIn(opt_dsl_code="", model={"name": "amdahl"})

    with pytest.raises(ValidationError):
        ApplicationScalingModelIn(opt_dsl_code="", model={"name": "noop", "F": 0.5})


def test_noop():
    """Test that the noop model always returns false"""

    appmodel_noop = ApplicationScalingModelIn(opt_dsl_code="", model={"name": "noop"})
    assert not appmodel_noop.model.scale(Application.construct())


def test_amdahl_basic():
    """Test that the Amdahl scaling model works"""

    amdahl = ScalingModelAmdahl(name="amdahl", F=0.5)
    app = Application.construct(mpi_ranks=256, minimal_efficiency=0.2)
    assert amdahl.scale(app)
    assert app.mpi_ranks == 9

    amdahl = ScalingModelAmdahl(name="amdahl", F=0.999)
    app = Application.construct(mpi_ranks=256, minimal_efficiency=0.8)
    assert amdahl.scale(app)
    assert app.mpi_ranks == 251


def test_amdahl_max():
    """Test that the Amdahl scaling model obeys the given max number of ranks"""

    amdahl = ScalingModelAmdahl(name="amdahl", F=0.999)
    app = Application.construct(mpi_ranks=256, minimal_efficiency=0.1)
    assert amdahl.scale(app)
    assert app.mpi_ranks == 256  # capped by the given number of mpi ranks


def test_amdahl_noop():
    """Test that the Amdahl scaling model doesn't do anything without an efficiency"""

    amdahl = ScalingModelAmdahl(name="amdahl", F=0.999)
    app = Application.construct(mpi_ranks=256)
    assert not amdahl.scale(app)  # without an efficiency Amdahl should not run


def test_amdahl_correctness():
    """Verify that the proposed number of ranks matches the scaling"""

    amdahl = ScalingModelAmdahl(name="amdahl", F=0.8)
    app = Application.construct(mpi_ranks=256, minimal_efficiency=0.5)
    assert amdahl.scale(app)
    assert app.mpi_ranks < 256
    assert app.mpi_ranks > 1
    assert amdahl.efficiency(app.mpi_ranks) == pytest.approx(0.5, 1e-6)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_scaler_no_dsl_code(driver):
    scaler = Scaler(driver, Mapper(driver))
    app = Application.construct(app_tag="testapp", mpi_ranks=256)
    assert not await scaler.scale(app)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_scaler_no_model(driver):

    stmt = insert(db.Optimisation).values(
        opt_dsl_code="test01",
        app_name="testapp",
        target="enable_opt_build:false",
    )
    await driver.update_sql(stmt)

    scaler = Scaler(driver, Mapper(driver))
    app = Application.construct(app_tag="testapp", mpi_ranks=256)
    assert not await scaler.scale(app)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_scaler_max(driver):
    stmt = insert(db.Optimisation).values(
        opt_dsl_code="test01",
        app_name="testapp",
        target="enable_opt_build:false",
    )
    await driver.update_sql(stmt)

    MAX_NRANKS = 16
    MAX_NTHREADS = 4

    stmt = insert(db.ScalingModel).values(
        opt_dsl_code="test01",
        model={"name": "max", "max_nranks": MAX_NRANKS, "max_nthreads": MAX_NTHREADS},
    )
    await driver.update_sql(stmt)

    scaler = Scaler(driver, Mapper(driver))
    app = Application.construct(app_tag="testapp", mpi_ranks=256, threads=8)
    assert await scaler.scale(app)  # the scaling should run
    assert app.mpi_ranks == MAX_NRANKS
    assert app.threads == MAX_NTHREADS
