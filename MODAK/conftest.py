import pytest
from sqlalchemy import create_engine

from MODAK.db import Base


@pytest.fixture(name="dbengine")
def engine_fixture():
    """Create an empty in-memory database"""
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    yield engine
