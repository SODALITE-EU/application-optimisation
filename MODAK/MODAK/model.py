from datetime import timedelta
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import (
    AnyUrl,
    BaseModel,
    EmailStr,
    Extra,
    Field,
    PositiveInt,
    root_validator,
)


class JobOptions(BaseModel, extra=Extra.forbid):
    """Options to pass to the queueing system"""

    job_name: str = "job"
    wall_time_limit: Optional[timedelta]
    node_count: Optional[PositiveInt]
    request_gpus: Optional[PositiveInt]
    core_count: Optional[PositiveInt] = Field(
        description="core count to use when running this job. Passed to the queueing system."
    )
    process_count_per_node: PositiveInt = 1
    standard_output_file: str = "job.out"
    standard_error_file: Optional[str]
    combine_stdout_stderr: bool = True
    request_event_notification: Optional[str]
    email_address: Optional[EmailStr]
    copy_environment: Optional[bool]
    copy_environment_variable: Optional[str]
    request_specific_nodes: Optional[str]

    @root_validator
    def check_app_type(cls, values):  # noqa: B902
        """Enforce standard_error_file if combine_stdout_stderr is false"""

        if not values["combine_stdout_stderr"] and "standard_error_file" not in values:
            raise ValueError(
                "'standard_error_file' must be specified"
                " unless 'combine_stdout_stderr' is enabled"
            )

        return values

    @root_validator
    def check_email_for_notification(cls, values):  # noqa: B902
        """Check that an email_address is specified when event notification is requested"""

        if values["request_event_notification"] and "email_address" not in values:
            raise ValueError(
                "'email_address' must be specified when 'request_event_notification' is enabled"
            )

        return values


class JobSchedulerType(str, Enum):
    """Supported types of queueing systems."""

    slurm = "slurm"
    torque = "torque"


class ApplicationAppType(str, Enum):
    """Supported types of applications."""

    mpi = "mpi"
    hpc = "hpc"
    python = "python"


class Target(BaseModel):
    """
    Description of the target where this application is going to run.
    If nothing is specified only a Unix shell environment will be assumed.
    """

    job_scheduler_type: Optional[JobSchedulerType] = Field(
        description="The queuing system to target if the infrastructure name is not specified"
    )
    name: Optional[str] = Field(description="The target infrastructure")

    @root_validator
    def check_one(cls, values):  # noqa: B902
        """Check that exactly one of the 2 attributes is set"""

        if (values.get("job_scheduler_type") is None) and (values.get("name") is None):
            raise ValueError(
                "at least one of 'job_scheduler_type' and 'name' must be specified"
            )

        return values

    class Config:
        extra = "forbid"
        use_enum_values = True


class ApplicationBuild(BaseModel, extra=Extra.forbid):
    """Source and build commands for the application"""

    src: AnyUrl = Field(description="Source URL for the application" "")
    build_command: str = Field(
        description=(
            "commands (shell script) to build the application, use"
            " {{BUILD_PARALLELISM}} to obtain number of parallel build jobs"
        )
    )
    build_parallelism: PositiveInt = Field(
        1, description="Number of parallel build jobs"
    )


class Application(BaseModel):
    app_tag: Optional[str]  # TODO: unused
    app_type: Optional[ApplicationAppType] = Field(description="this applications type")
    executable: str
    arguments: Optional[str]
    container_runtime: Optional[str] = Field(
        description=(
            "Will be filled/overwritten in the response"
            " if an optimised container was found."
        )
    )
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
    build: Optional[ApplicationBuild] = Field(
        description=(
            "Build information in case on-site rebuilding of"
            " the application is desired and possible"
        )
    )

    class Config:
        extra = "forbid"
        use_enum_values = True


class OptimisationBuildCpuType(str, Enum):
    """Supported CPU ISAs"""

    x86 = "x86"
    arm = "arm"
    amd = "amd"
    power = "power"


class OptimisationBuildAccType(str, Enum):
    """Supported accelerators"""

    nvidia = "nvidia"
    amd = "amd"
    fpga = "fpga"


class OptimisationBuild(BaseModel):
    cpu_type: OptimisationBuildCpuType = Field(
        description="The CPU to optimise the build for"
    )
    acc_type: Optional[OptimisationBuildAccType] = Field(
        description="The accelerator to optimise the build for"
    )

    class Config:
        extra = "forbid"
        use_enum_values = True


class HPCConfigParallelisation(str, Enum):
    """Supported parallelisations"""

    mpi = "mpi"
    openmp = "openmp"
    opencc = "opencc"
    opencl = "opencl"


class HPCConfig(BaseModel):
    parallelisation: HPCConfigParallelisation = Field(
        description="Parallelisation used in this HPC application"
    )

    class Config:
        extra = "forbid"
        use_enum_values = True


class ParallelisationMpi(BaseModel, extra=Extra.forbid):
    library: str
    version: str


# TODO: define for openmp, opencc, opencl based on TOSCA/DSL
class AppTypeHPC(BaseModel, extra=Extra.forbid):
    """HPC-specific configuration for optimisation"""

    config: HPCConfig
    data: Dict[str, Any] = Field(  # TODO: specified in TOSCA/DSL
        default_factory=dict, description="Application specific data"
    )
    parallelisation_mpi: ParallelisationMpi = Field(..., alias="parallelisation-mpi")

    @root_validator
    def check_app_type(cls, values):  # noqa: B902
        """Ensure that for a given parallelisation there is a parallelisation-* submodel."""

        try:
            parallelisation_name = values["config"].parallelisation
        except KeyError:
            # the mandatory attribute verification comes after this,
            # ignore this error and skip rest of the checks
            return values

        parallelisation_sec = f"parallelisation-{parallelisation_name}"
        if not values.get(parallelisation_sec.replace("-", "_")):
            raise ValueError(
                f"Required section '{parallelisation_sec}' not found"
                f" for config/parallelisation '{parallelisation_name}'"
            )
        return values


# TODO: Keras & Pytorch based on TOSCA/DSL
class AIFrameworkTensorflow(BaseModel, extra=Extra.forbid):
    version: str
    xla: bool


class AITrainingConfigFramework(str, Enum):
    tensorflow = "tensorflow"
    pytorch = "pytorch"
    keras = "keras"
    cntk = "cntk"
    mxnet = "mxnet"


class AITrainingConfig(BaseModel):
    ai_framework: AITrainingConfigFramework
    # DSL has type: str/enum here # TODO: unused
    # DSL has distributed_training: bool  # TODO" unused

    class Config:
        extra = "forbid"
        use_enum_values = True


class AppTypeAITraining(BaseModel, extra=Extra.forbid):
    config: AITrainingConfig
    data: Dict[str, Any] = Field(  # TODO: in TOSCA?DSL specified but unused
        default_factory=dict, description="Application specific data"
    )
    ai_framework_tensorflow: AIFrameworkTensorflow = Field(
        ..., alias="ai_framework-tensorflow"
    )

    @root_validator
    def check_app_type(cls, values):  # noqa: B902
        """Ensure that for a given ai_framework there is a ai_framework-* submodel."""
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


class OptimisationAutotuning(BaseModel, extra=Extra.forbid):
    tuner: str
    input: str


class OptimisationAppType(str, Enum):
    """Supported application types for optimisation."""

    ai_training = "ai_training"
    hpc = "hpc"
    # TODO: big_data, ai_inference


class Optimisation(BaseModel):
    enable_opt_build: bool
    enable_autotuning: bool = False
    app_type: OptimisationAppType = Field(description="Application type")
    opt_build: Optional[OptimisationBuild]
    app_type_hpc: Optional[AppTypeHPC] = Field(alias="app_type-hpc")
    app_type_ai_training: Optional[AppTypeAITraining] = Field(
        alias="app_type-ai_training"
    )
    autotuning: Optional[OptimisationAutotuning]

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

    class Config:
        extra = "forbid"
        use_enum_values = True


class Job(BaseModel, extra=Extra.forbid):
    """The toplevel Job object"""

    job_options: JobOptions
    target: Optional[Target]
    application: Application
    optimisation: Optional[Optimisation]
    job_script: Optional[str] = Field(
        description="A link to the job script generated for the request"
    )
    build_script: Optional[str] = Field(
        description="The content of the build script generated for the request"
    )
    job_content: Optional[str] = Field(
        description="The content of the job script generated for the request"
    )
    build_content: Optional[str] = Field(
        description="The content of the build script generated for the request"
    )


class JobModel(BaseModel):
    job: Job

    class Config:
        title = "MODAK Job schema"
        extra = "forbid"


class ScriptConditions(BaseModel):
    pass


class ScriptData(BaseModel):
    pass


class Script(BaseModel):
    id: UUID
    description: str
    conditions: ScriptConditions
    data: ScriptData

    class Config:
        orm_mode = True


class ScriptIn(BaseModel):
    description: str
    conditions: ScriptConditions
    data: ScriptData


class ScriptList(BaseModel):
    id: UUID
    description: str
    conditions: ScriptConditions

    class Config:
        orm_mode = True
