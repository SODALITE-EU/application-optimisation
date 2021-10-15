#!/usr/bin/env python3

import pathlib

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from MODAK.MODAK import MODAK
from MODAK.model import JobModel

BASE_PATH = pathlib.Path(__file__).resolve().parent
app = FastAPI(title="MODAK Application Optimizer")
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))


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
def modak_get_optimisation(model: JobModel):
    m = MODAK()
    model.job.application.container_runtime, model.job.job_content = m.get_optimisation(
        model.job
    )
    return model
