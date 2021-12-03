import pytest
from sqlalchemy import create_engine

from MODAK.db import Base
from MODAK.driver import Driver


@pytest.fixture(name="dbengine")
def engine_fixture():
    """Create an empty in-memory database"""
    engine = create_engine("sqlite://", future=True, echo=True)
    Base.metadata.create_all(engine)
    yield engine


@pytest.fixture(name="modak_driver")
def modak_driver_fixture(dbengine):
    """Get a Driver instance tied to an in-memory DB engine"""
    yield Driver(dbengine)
