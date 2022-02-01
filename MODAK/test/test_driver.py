import pytest
from sqlalchemy import select

from MODAK.db import Optimisation
from MODAK.driver import Driver


@pytest.fixture
def driver():
    """Create a driver with the test DB"""
    driver = Driver()
    yield driver


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_driver(driver):
    data = await driver.select_sql(
        select(Optimisation.opt_dsl_code, Optimisation.app_name).where(
            Optimisation.app_name == "pytorch"
        )
    )
    assert data[0][1] == "pytorch"
