import abc
from typing import Literal, Optional, Union

from pydantic import Field, PositiveInt

from . import Application, BaseModel


class ScalingModel(BaseModel, abc.ABC):
    """Supported scaling models"""

    name: Literal["model"]

    @abc.abstractmethod
    def scale(self, app: Application) -> bool:
        """Apply scaling to application"""
        pass


class ScalingModelNoop(ScalingModel):
    """No-op scaling model, mostly for testing"""

    name: Literal["noop", "no-op"]

    def scale(self, _: Application) -> bool:
        """The no-op never does anything."""
        return False


class ScalingModelMax(ScalingModel):
    """Put a limit on specified properties"""

    name: Literal["max"]
    max_nranks: Optional[PositiveInt] = Field(
        None, description="The max number ranks the app should use"
    )
    max_nthreads: Optional[PositiveInt] = Field(
        None, description="The max number of threads the app should use"
    )

    def scale(self, app: Application) -> bool:
        """Update the given Job, returns True if modified, False otherwise."""

        changed = False

        if self.max_nranks:
            app.mpi_ranks = min(app.mpi_ranks, self.max_nranks)
            changed = True

        if self.max_nthreads:
            app.threads = min(app.threads, self.max_nthreads)
            changed = True

        return changed


class ScalingModelAmdahl(ScalingModel):
    """Amdahls Law"""

    name: Literal["amdahl"]
    F: float = Field(..., description="the parallel efficiency coefficient")

    def scale(self, app: Application) -> bool:
        """Update the given Job, returns True if modified, False otherwise."""

        if app.minimal_efficiency is None:
            return False

        app.mpi_ranks = min(app.mpi_ranks, self._nranks(app.minimal_efficiency))
        return True

    def _nranks(self, Eff: float) -> int:
        return round((1 - Eff * self.F) / (Eff * (1 - self.F)))

    def efficiency(self, nranks):
        return 1 / (nranks * (1 - self.F) + self.F)


class ApplicationScalingModel(BaseModel):
    """A scaling model for a given application, resp. container, defined by name and parameters."""

    opt_dsl_code: str = Field(
        ..., description="The DSL code of the container for which this model holds"
    )
    model: Union[ScalingModelNoop, ScalingModelMax, ScalingModelAmdahl]

    class Config:
        orm_mode = True
