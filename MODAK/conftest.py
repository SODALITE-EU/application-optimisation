import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from MODAK.db import Base
from MODAK.driver import Driver


@pytest.fixture(name="driver")
async def modak_driver_fixture():
    """Get a Driver instance tied to an in-memory DB engine"""

    engine = create_async_engine("sqlite+aiosqlite://", future=True, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield Driver(engine)
