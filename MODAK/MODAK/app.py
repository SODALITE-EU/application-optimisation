#!/usr/bin/env python3

import pathlib
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from MODAK.db import Script as ScriptDB
from MODAK.MODAK import MODAK
from MODAK.model import JobModel, Script, ScriptIn, ScriptList
from MODAK.settings import Settings

BASE_PATH = pathlib.Path(__file__).resolve().parent
app = FastAPI(title="MODAK Application Optimizer")
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

engine = create_async_engine(f"sqlite+aiosqlite:///{Settings.db_path}", future=True)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
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


# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             session['logged_in'] = True
#             return redirect(url_for('home'))
#
#     return render_template('login.html', error=error)
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('home'))


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


@app.get("/scripts", response_model=List[ScriptList])
async def list_scripts(session: AsyncSession = Depends(get_db_session)):  # noqa: B008
    """List all registered scripts"""
    result = await session.execute(select(ScriptDB))
    return result.scalars().all()


@app.get("/scripts/{script_id}", response_model=Script)
async def get_script(
    script_id: UUID, session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    """Get script"""
    result = await session.execute(select(ScriptDB).where(ScriptDB.id == script_id))

    try:
        return result.scalars().one()
    except NoResultFound:
        raise HTTPException(404)


@app.post("/scripts", response_model=ScriptList, status_code=201)
async def create_script(
    script_in: ScriptIn, session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    """Add a new script"""

    dbobj = ScriptDB(**script_in.dict())

    async with session.begin():
        session.add(dbobj)

    return dbobj
