"""Routines to create DB objects from Schema instances"""

from typing import cast

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from . import db, model


class ConstraintFailureError(Exception):
    pass


async def create_script(session: AsyncSession, script_in: model.ScriptIn) -> db.Script:
    try:
        infrastructure_name = cast(
            model.ScriptConditionApplication, script_in.conditions.infrastructure
        ).name

        result = await session.execute(
            select(db.Infrastructure).where(
                db.Infrastructure.name == infrastructure_name
            )
        )
        result.one()  # will raise if not found
    except AttributeError:
        pass
    except NoResultFound:
        raise ConstraintFailureError(
            f"Infrastructure named '{infrastructure_name}' not found"
        ) from None

    return db.Script(**script_in.dict())
