"""Routines to create DB objects from Schema instances"""

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from . import db
from .model import ContainerMapping, OptimisationBuild, ScriptIn
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


def _defstr_to_dict(defstr: Optional[str]) -> Dict[str, Any]:
    if defstr is None:
        return dict()

    def formatted(val) -> Any:
        if val == "none":
            return None

        if val in ("true", "false"):
            return True

        if val == "false":
            return False

        return val

    return {k: formatted(v) for k, v in (t.split(":") for t in defstr.split("|") if t)}


def container_mapping_from_db(
    opt: db.Optimisation, mapping: db.Map
) -> ContainerMapping:
    target = _defstr_to_dict(opt.target)
    enable_opt_build = bool(target.get("enable_opt_build", False))
    del target["enable_opt_build"]

    selectors = _defstr_to_dict(opt.optimisation)

    return ContainerMapping(
        opt_dsl_code=opt.opt_dsl_code,
        app_name=opt.app_name,
        version=opt.version,
        enable_opt_build=enable_opt_build,
        target=OptimisationBuild(**target),
        selectors=selectors,
        container_name=mapping.container_file,
        container_type=mapping.image_type,
        container_registry=mapping.image_hub,
    )
