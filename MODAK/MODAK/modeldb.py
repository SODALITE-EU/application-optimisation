"""Routines to create DB objects from Schema instances"""

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from . import db
from .model import ScriptIn
from .model.infrastructure import InfrastructureConfiguration


class ConstraintFailureError(Exception):
    pass


async def create_script(session: AsyncSession, script_in: ScriptIn) -> db.Script:
    if script_in.conditions.infrastructure and script_in.conditions.infrastructure.name:
        result = await session.execute(
            select(db.Infrastructure).where(
                db.Infrastructure.name == script_in.conditions.infrastructure.name
            )
        )
        try:
            infra = result.scalars().one()
        except NoResultFound:
            raise ConstraintFailureError(
                f"No infrastructure found for: {script_in.conditions.infrastructure.name}"
            ) from None

        if script_in.conditions.infrastructure.storage_class:
            iconf = InfrastructureConfiguration(**infra.configuration)
            if not any(
                script_in.conditions.infrastructure.storage_class == s.storage_class
                for s in iconf.storage.values()
            ):
                raise ConstraintFailureError(
                    f"The specified infrastructure '{script_in.conditions.infrastructure.name}' does not have a storage location"
                    f" with the given storage_class: {script_in.conditions.infrastructure.storage_class}"
                ) from None

    if script_in.conditions.application and script_in.conditions.application.name:
        result = await session.execute(
            select(db.Optimisation).where(
                db.Optimisation.app_name == script_in.conditions.application.name
            )
        )
        try:
            result.scalars().one()
        except NoResultFound:
            raise ConstraintFailureError(
                f"No application found for: {script_in.conditions.application.name}"
            ) from None

    return db.Script(**script_in.dict())
