import pathlib
import re
from copy import deepcopy
from unittest.mock import patch

import pytest

from MODAK.MODAK import MODAK
from MODAK.model import Application, Job, JobModel, JobOptions

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


def _tsreplaced(content):
    """Replace timestamps consisting of 14 digits in the given content."""
    return re.sub(r"\d{14}", 14 * "X", content)


@pytest.mark.xfail  # Tuner not yet enabled
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_modak_hpc():
    print("Test MODAK")
    m = MODAK()
    dsl_file = SCRIPT_DIR / "input" / "mpi_solver.json"
    model = JobModel.parse_raw(dsl_file.read_text())
    job_link = await m.optimise(model.job)

    assert _tsreplaced(
        SCRIPT_DIR.joinpath("input/solver.sh").read_text()
    ) == _tsreplaced(pathlib.Path(job_link.jobscript).read_text())


@pytest.mark.xfail  # Tuner not yet enabled
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_modak_ai():
    print("Test MODAK")
    m = MODAK()
    dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"
    model = JobModel.parse_raw(dsl_file.read_text())
    job_link = await m.optimise(model.job)

    assert _tsreplaced(
        SCRIPT_DIR.joinpath("input/skyline-extraction-training.sh").read_text()
    ) == _tsreplaced(pathlib.Path(job_link.jobscript).read_text())


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_modak_resnet():
    print("Test MODAK")
    m = MODAK()
    dsl_file = SCRIPT_DIR / "input" / "tf_resnet.json"
    model = JobModel.parse_raw(dsl_file.read_text())
    job_link = await m.optimise(model.job)

    assert _tsreplaced(
        SCRIPT_DIR.joinpath("input/resnet.sh").read_text()
    ) == _tsreplaced(pathlib.Path(job_link.jobscript).read_text())


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_modak_xthi():
    print("Test MODAK")
    m = MODAK()
    dsl_file = SCRIPT_DIR / "input" / "mpi_test.json"
    model = JobModel.parse_raw(dsl_file.read_text())
    job_link = await m.optimise(model.job)

    assert _tsreplaced(
        SCRIPT_DIR.joinpath("input/mpi_test.sh").read_text()
    ) == _tsreplaced(pathlib.Path(job_link.jobscript).read_text())


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_modak_egi_xthi():
    print("Test MODAK")
    m = MODAK()
    dsl_file = SCRIPT_DIR / "input" / "mpi_test_egi.json"
    model = JobModel.parse_raw(dsl_file.read_text())
    job_link = await m.optimise(model.job)

    assert _tsreplaced(
        SCRIPT_DIR.joinpath("input/mpi_test_egi.sh").read_text()
    ) == _tsreplaced(pathlib.Path(job_link.jobscript).read_text())


FAKE__GET_OPTIMISATION_VALUE = "#! /bin/sh\n# some build script"


async def fake__get_optimisation(*args, **_):
    args[1].write(FAKE__GET_OPTIMISATION_VALUE)
    return None


@patch("MODAK.MODAK.MODAK._get_optimisation")
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_minimal_no_build(_):
    """
    Tests a minimal job (with no build section)
    """
    job = Job.construct(
        job_options=JobOptions.parse_obj(
            {
                "job_name": "test_job",
                "node_count": 4,
                "process_count_per_node": 2,
                "standard_output_file": "test.out",
                "standard_error_file": "test.err",
                "combine_stdout_stderr": "true",
            }
        ),
        application=Application.parse_obj(
            {
                "executable": "./foo",
            }
        ),
    )
    expected_return = ""
    return_value = await MODAK().get_buildjob(job)

    assert expected_return == return_value


@patch("MODAK.MODAK.MODAK._get_optimisation")
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_minimal_build(mock__get_optimisation):
    """
    Tests a minimal job (with a build section)
    """

    mock__get_optimisation.side_effect = fake__get_optimisation

    job = Job.construct(
        job_options=JobOptions.parse_obj(
            {
                "job_name": "test_job",
                "node_count": 4,
                "process_count_per_node": 2,
                "standard_output_file": "test.out",
                "standard_error_file": "test.err",
                "combine_stdout_stderr": "true",
            }
        ),
        application=Application.parse_obj(
            {
                "executable": "./foo",
                "build": {
                    "build_command": "sleep 1",
                    "src": "git://example/git/repo.git",
                },
            }
        ),
    )
    return_value = await MODAK().get_buildjob(job)

    calljob = deepcopy(job)
    calljob.job_options.job_name = "test_job_build"
    calljob.job_options.node_count = 1
    calljob.job_options.process_count_per_node = 1
    calljob.job_options.standard_output_file = "build-test.out"
    calljob.job_options.standard_error_file = "build-test.err"
    calljob.application.executable = "git clone git://example/git/repo.git\nsleep 1"
    assert return_value == FAKE__GET_OPTIMISATION_VALUE
    mock__get_optimisation.assert_called_once()
    assert mock__get_optimisation.call_args.args[0] == calljob


@patch("MODAK.MODAK.MODAK._get_optimisation")
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_copy_environment(mock__get_optimisation):
    """
    Tests a minimal job (with a build section)
    """
    mock__get_optimisation.side_effect = fake__get_optimisation

    job = Job.construct(
        job_options=JobOptions.parse_obj(
            {
                "job_name": "test_job",
                "node_count": 4,
                "process_count_per_node": 2,
                "standard_output_file": "test.out",
                "standard_error_file": "test.err",
                "combine_stdout_stderr": "true",
                "copy_environment": "false",
            }
        ),
        application=Application.parse_obj(
            {
                "executable": "./foo",
                "build": {
                    "build_command": "sleep 1",
                    "src": "git://example/git/repo.git",
                },
            }
        ),
    )
    await MODAK().get_buildjob(job)

    assert not mock__get_optimisation.call_args.args[0].job_options.copy_environment


@patch("MODAK.MODAK.MODAK._get_optimisation")
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_non_git_src(mock__get_optimisation):
    """
    Tests a minimal job (with a build section)
    """
    mock__get_optimisation.side_effect = fake__get_optimisation

    job = Job.construct(
        job_options=JobOptions.parse_obj(
            {
                "job_name": "test_job",
                "node_count": 4,
                "process_count_per_node": 2,
                "standard_output_file": "test.out",
                "standard_error_file": "test.err",
                "combine_stdout_stderr": "true",
                "copy_environment": "false",
            }
        ),
        application=Application.parse_obj(
            {
                "executable": "./foo",
                "build": {
                    "build_command": "sleep 1",
                    "src": "http://example/tar.gz",
                },
            }
        ),
    )
    await MODAK().get_buildjob(job)

    assert (
        "wget --no-check-certificate 'http://example/tar.gz'\nsleep 1"
        == mock__get_optimisation.call_args.args[0].application.executable
    )


@patch("MODAK.MODAK.MODAK._get_optimisation")
@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_build_parallelism(mock__get_optimisation):
    """
    Tests a minimal job (with a build section)
    """
    mock__get_optimisation.side_effect = fake__get_optimisation

    job = Job.construct(
        job_options=JobOptions.parse_obj(
            {
                "job_name": "test_job",
                "node_count": 4,
                "process_count_per_node": 2,
                "standard_output_file": "test.out",
                "standard_error_file": "test.err",
                "combine_stdout_stderr": "true",
                "copy_environment": "false",
            }
        ),
        application=Application.parse_obj(
            {
                "executable": "./foo",
                "build": {
                    "build_command": "sleep {{BUILD_PARALLELISM}}",
                    "src": "http://example/tar.gz",
                    "build_parallelism": 4,
                },
            }
        ),
    )
    await MODAK().get_buildjob(job)

    # get_buildjob() should take the original job as a template
    # and replace the executable with the build command
    assert (
        "wget --no-check-certificate 'http://example/tar.gz'\nsleep 4"
        == mock__get_optimisation.call_args.args[0].application.executable
    )
