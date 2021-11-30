from enum import Enum
from typing import Optional

import archspec.cpu
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, validator
from pydantic.types import PositiveInt

# Use the CPU families from archspec as the base CPU architecture
CPUArch = Enum(  # type: ignore # Ref: python/mypy#529, #535 and #5317
    "CPUArch",
    {name: name for name, march in archspec.cpu.TARGETS.items() if not march.parents},
    type=str,
)

# For the Microarchitecture, use the non-generic, non-family entries
CPUMicroArch = Enum(  # type: ignore # Ref: python/mypy#529, #535 and #5317
    "CPUMicroArch",
    {
        name: name
        for name, march in archspec.cpu.TARGETS.items()
        if march.parents and march.vendor != "generic"
    },
    type=str,
)


class CPU(PydanticBaseModel):
    arch: CPUArch = Field(..., description="CPU architecture")
    # Overlap of arch with microarch is intended since Docker classifies compatibility
    # into broader categories rather than microarchitectures.
    microarch: Optional[CPUMicroArch] = Field(
        description="Microarchitecture, must match the architecture if specified"
    )
    ncores: PositiveInt = Field(..., description="Number of cores per CPU")
    nthreads: PositiveInt = Field(1, description="Number of threads (per core)")

    @validator("microarch")
    def microarch_matches_arch(cls, v, values, **kwargs):  # noqa: B902
        if not (archspec.cpu.TARGETS[values["arch"]] < archspec.cpu.TARGETS[v]):
            raise ValueError(
                f"invalid microarchitecture '{v}' for architecture '{values['arch']}'"
            )
        return v
