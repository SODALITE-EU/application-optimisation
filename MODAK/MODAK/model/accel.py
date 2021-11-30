from enum import Enum

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class AccleratorTypes(str, Enum):
    """Supported accelerator types"""

    gpu = "gpu"
    fpga = "fpga"
    tpu = "tpu"


class Accelerator(PydanticBaseModel):
    type: AccleratorTypes = Field(..., description="Accelerator type")
    model: str
