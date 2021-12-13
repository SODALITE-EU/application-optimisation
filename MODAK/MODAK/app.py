#!/usr/bin/env python3

import pathlib
from typing import AsyncIterator, List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from MODAK import db
from MODAK.MODAK import MODAK
from MODAK.model import JobModel, Script, ScriptIn
from MODAK.model.infrastructure import Infrastructure, InfrastructureIn
from MODAK.settings import Settings

from . import modeldb, oidc_helpers

BASE_PATH = pathlib.Path(__file__).resolve().parent
app = FastAPI(title="MODAK Application Optimizer")
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

authentication_token = oidc_helpers.ExtendedOpenIdConnect(
    client_id="modak",
    base_authorization_server_url=Settings.oidc_auth_url,
    signature_cache_ttl=3600,
    api_key=Settings.api_key,
)

engine = create_async_engine(f"sqlite+aiosqlite:///{Settings.db_path}", future=True)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@app.post("/optimise", response_model=JobModel, response_model_exclude_none=True)
async def optimise(model: JobModel):
    m = MODAK()
    model.job.job_script, model.job.build_script = m.optimise(model.job)
    return model


@app.post("/get_image", response_model=JobModel, response_model_exclude_none=True)
async def get_image(model: JobModel):
    m = MODAK()
    container_runtime = m.get_opt_container_runtime(model.job)
    model.job.application.container_runtime = container_runtime
    return model


@app.post("/get_build", response_model=JobModel, response_model_exclude_none=True)
async def get_build(model: JobModel):
    m = MODAK()
    model.job.build_script = m.get_buildjob(model.job)
    return model


@app.post(
    "/get_optimisation", response_model=JobModel, response_model_exclude_none=True
)
async def modak_get_optimisation(model: JobModel):
    m = MODAK()
    model.job.application.container_runtime, model.job.job_content = m.get_optimisation(
        model.job
    )
    return model


@app.get("/scripts", response_model=List[Script], response_model_exclude_none=True)
async def list_scripts(session: AsyncSession = Depends(get_db_session)):  # noqa: B008
    """List all registered scripts"""
    result = await session.execute(select(db.Script))
    return result.scalars().all()


@app.get(
    "/scripts/{script_id}", response_model=Script, response_model_exclude_none=True
)
async def get_script(
    script_id: UUID, session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    """Get script"""
    result = await session.execute(select(db.Script).where(db.Script.id == script_id))

    try:
        return result.scalars().one()
    except NoResultFound:
        raise HTTPException(404) from None


@app.post(
    "/scripts",
    response_model=Script,
    status_code=201,
    response_model_exclude_none=True,
    dependencies=[Depends(authentication_token)],
)
async def create_script(
    script_in: ScriptIn, session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    """Add a new script"""
    async with session.begin():
        try:
            dbobj = await modeldb.create_script(session, script_in)
        except modeldb.ConstraintFailureError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from None
        session.add(dbobj)

    return dbobj


@app.get(
    "/infrastructures",
    response_model=List[Infrastructure],
    response_model_exclude_none=True,
)
async def list_infrastructures(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
):
    """List all registered infrastructures"""
    result = await session.execute(select(db.Infrastructure))
    return result.scalars().all()


@app.get(
    "/infrastructures/{infrastructure_id}",
    response_model=Infrastructure,
    response_model_exclude_none=True,
)
async def get_infrastructure(
    infrastructure_id: UUID,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
):
    """Get infrastructure details"""
    result = await session.execute(
        select(db.Infrastructure).where(db.Infrastructure.id == infrastructure_id)
    )

    try:
        return result.scalars().one()
    except NoResultFound:
        raise HTTPException(404) from None


@app.post(
    "/infrastructures",
    response_model=Infrastructure,
    status_code=201,
    response_model_exclude_none=True,
    dependencies=[Depends(authentication_token)],
)
async def create_infrastructure(
    infrastructure_in: InfrastructureIn,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
):
    """Add a new infrastructure"""

    dbobj = db.Infrastructure(**infrastructure_in.dict())

    async with session.begin():
        session.add(dbobj)
    return dbobj
