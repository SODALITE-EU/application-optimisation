from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import ByteSize, Field, PositiveInt, root_validator

from . import BaseModel, JobSchedulerType
from .accel import Accelerator
from .cpu import CPU
from .storage import StorageMapMixin


class Node(StorageMapMixin, BaseModel):
    """Basic hardware description of a node."""

    # The full configuration (NUMA model) is deliberately not included for now.
    # TODO: support mixed-{accelerator,cpu,memory} node types.
    ncpus: PositiveInt = Field(
        ..., description="Number of CPUs (populated sockets) in this system"
    )
    cpu: CPU = Field(..., description="CPU description")
    naccel: Optional[PositiveInt] = Field(
        description="Number of accelerators connected to a node"
    )
    accel: Optional[Accelerator] = Field(description="Accelerator description")
    memory: ByteSize = Field(description="Amount of memory available on a node")

    @root_validator
    def accel_defined(cls, values):  # noqa: B902
        """Ensures that accelerator information is given if naccel > 0"""

        if (values.get("naccel") is None) ^ (values.get("accel") is None):
            raise ValueError(
                "naccel and accel have to be both defined or both undefined"
            )

        return values


class InfrastructurePartition(StorageMapMixin, BaseModel):
    nnodes: PositiveInt = Field(..., description="Number of nodes in this partition")
    node: Node = Field(..., description="Configuration of the nodes in the partition")


class InfrastructureConfiguration(StorageMapMixin, BaseModel):
    """Minimal configuration required for an infrastructure."""

    # Compared to the full proposal in
    #   https://github.com/SODALITE-EU/application-optimisation/issues/3#issuecomment-640577805
    # we include only a minimal subset for now: the scheduler required to automatically
    # generate run scripts and the storage to include staging/broadcasting steps in the script.
    scheduler: Optional[JobSchedulerType] = Field(
        description="(default) queueing system type running on the infrastructure (if any)"
    )
    partitions: Dict[str, InfrastructurePartition] = Field(
        default_factory=dict,
        description="Mapping of partitions, use '*' for a single (default) partition",
    )

    class Config:
        schema_extra = {
            "example": {
                "scheduler": "slurm",
                "storage": {
                    "file:///scratch": {
                        "storage_class": "default-high",
                    },
                    "file:///data": {
                        "storage_class": "common",
                    },
                },
                "partitions": {
                    "mc": {
                        "nnodes": 100,
                        "node": {
                            "ncpus": 2,
                            "cpu": {
                                "arch": "x86_64",
                                "microarch": "zen2",
                                "ncores": 64,
                                "nthreads": 2,
                            },
                            "naccel": 0,
                            "memory": "512GiB",
                        },
                    },
                    "gpu": {
                        "nnodes": 5,
                        "node": {
                            "ncpus": 1,
                            "cpu": {
                                "arch": "x86_64",
                                "microarch": "zen2",
                                "ncores": 32,
                                "nthreads": 2,
                            },
                            "naccel": 2,
                            "accel": {
                                "type": "gpu",
                                "model": "P100",
                            },
                            "memory": "256GiB",
                        },
                    },
                },
            },
        }


class InfrastructureIn(BaseModel):
    name: str
    disabled: Optional[datetime] = Field(
        description=(
            "Time and date at which this infrastructure has been or will be disabled"
            " (if not set, infrastructure is enabled)"
        )
    )
    description: Optional[str]
    configuration: InfrastructureConfiguration


class Infrastructure(InfrastructureIn):
    id: UUID

    class Config:
        orm_mode = True
