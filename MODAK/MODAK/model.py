from datetime import timedelta
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Field, PositiveInt, root_validator


class JobOptions(BaseModel):
    job_name: str
    wall_time_limit: timedelta
    node_count: PositiveInt
    core_count: Optional[PositiveInt] = Field(
        description="core count to use when running this job. Passed to the queueing system."
    )
    process_count_per_node: PositiveInt
    standard_output_file: str
    standard_error_file: str
    combine_stdout_stderr: bool
    request_event_notification: str
    email_address: EmailStr


class JobSchedulerTypeEnum(str, Enum):
    """Type of queueing system."""

    slurm = "slurm"
    torque = "torque"


class ApplicationAppTypeEnum(str, Enum):
    """Type of application."""

    mpi = "mpi"
    hpc = "hpc"


class Target(BaseModel):
    """
    Description of the target where this application is going to run.
    If not specified only a Unix shell environment (possibly with mpirun) will be assumed.
    """

    job_scheduler_type: JobSchedulerTypeEnum
    name: Optional[str] = Field(
        description="Additional keyword to select specific optimisations"
    )

    class Config:
        extra = "forbid"


class ApplicationBuild(BaseModel):
    """Source and build commands for the application"""

    src: AnyUrl
    build_command: str

    class Config:
        extra = "forbid"


class Application(BaseModel):
    app_tag: str
    app_type: ApplicationAppTypeEnum
    executable: str
    arguments: Optional[str]
    mpi_ranks: PositiveInt = Field(
        1,  # default
        description=(
            "Number of MPI ranks to use when running the application as part of a job."
            " Passed to mpirun or srun."
        ),
    )
    threads: PositiveInt = Field(
        1,  # default
        description=(
            "Number of OpenMP threads to use when running the application as part of a job."
            " Set before mpirun or srun."
        ),
    )
    build: Optional[ApplicationBuild]

    class Config:
        extra = "forbid"


class OptimisationBuild(BaseModel):
    cpu_type: str
    acc_type: str

    class Config:
        extra = "forbid"


class HPCConfig(BaseModel):
    parallelisation: str

    class Config:
        extra = "forbid"


class ParallelisationMpi(BaseModel):
    library: str
    version: str

    class Config:
        extra = "forbid"


class AppTypeHPC(BaseModel):
    config: HPCConfig
    data: Dict[str, Any] = Field(
        default_factory=Dict, description="Application specific data (not formalized)"
    )
    parallelisation_mpi: ParallelisationMpi = Field(..., alias="parallelisation-mpi")

    class Config:
        extra = "forbid"


class AIFrameworkTensorflow(BaseModel):
    version: str
    xla: bool

    class Config:
        extra = "forbid"


class AITrainingConfig(BaseModel):
    ai_framework: str

    class Config:
        extra = "forbid"


class AppTypeAITraining(BaseModel):
    config: AITrainingConfig
    data: Dict[str, Any] = Field(
        default_factory=Dict, description="Application specific data (not formalized)"
    )
    ai_framework_tensorflow: AIFrameworkTensorflow = Field(
        ..., alias="ai_framework-tensorflow"
    )

    class Config:
        extra = "forbid"

    @root_validator
    def check_app_type(cls, values):  # noqa: B902
        try:
            ai_framework_name = values["config"].ai_framework
        except KeyError:
            # the mandatory attribute verification comes after this,
            # ignore this error and skip rest of the checks
            return values

        ai_framework_sec = f"ai_framework-{ai_framework_name}"
        if not values.get(ai_framework_sec.replace("-", "_")):
            raise ValueError(
                f"Required section '{ai_framework_sec}' not found"
                f" for config/ai_framework '{ai_framework_name}'"
            )
        return values


class OptimisationAutotuning(BaseModel):
    tuner: str
    input: str

    class Config:
        extra = "forbid"


class Optimisation(BaseModel):
    enable_opt_build: bool
    enable_autotuning: Optional[bool] = False
    app_type: str
    opt_build: OptimisationBuild
    app_type_hpc: Optional[AppTypeHPC] = Field(alias="app_type-hpc")
    app_type_ai_training: Optional[AppTypeAITraining] = Field(
        alias="app_type-ai_training"
    )
    autotuning: Optional[OptimisationAutotuning]

    class Config:
        extra = "forbid"

    @root_validator
    def check_app_type(cls, values):  # noqa: B902
        app_type_attr = f"app_type-{values['app_type']}"
        if not values.get(app_type_attr.replace("-", "_")):
            raise ValueError(
                f"Required section '{app_type_attr}' not found"
                f" for app_type '{values['app_type']}'"
            )

        if values.get("app_type_hpc") and values.get("app_type_ai_training"):
            raise ValueError("The app_type-* attributes are mutually exclusive")

        return values


class Job(BaseModel):
    """The toplevel Job object"""

    job_options: JobOptions
    target: Optional[Target]
    application: Application
    optimisation: Optimisation

    class Config:
        extra = "forbid"


class JobModel(BaseModel):
    job: Job

    class Config:
        title = "MODAK Job schema"
        extra = "forbid"
