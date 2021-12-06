from enum import Enum
from typing import Dict
from urllib.parse import urlparse

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, validator

ALLOWED_DEFAULT_SUFFIXES = ("common", "high", "ssd", "ultra_high")


class DefaultStorageClass(str, Enum):
    """Allowed default storage class values"""

    _ignore_ = "suffix prefix"

    prefix = "default"
    for suffix in ALLOWED_DEFAULT_SUFFIXES:
        vars()[f"{prefix}_{suffix.replace('-', '_')}"] = f"{prefix}-{suffix}"

    @property
    def idx(self):
        return ALLOWED_DEFAULT_SUFFIXES.index(self.value.split("-")[1])

    def __gt__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.idx > other.idx

    def __ge__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.idx >= other.idx

    def __le__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.idx <= other.idx

    def __lt__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.idx < other.idx


class StorageConfiguration(PydanticBaseModel):
    """A single storage location description."""

    storage_class: str = Field(..., description="Storage class of this storage")

    @validator("storage_class")
    def storage_class_defaults(cls, v):  # noqa: B902
        """If the storage_class has a 'default-' prefix, we validate the suffix against
        a list of well-known storage classes"""

        ALLOWED_PREFIXES = ("default",)

        try:
            prefix, _ = v.split("-", maxsplit=1)
        except ValueError:
            raise ValueError(
                f"The storage_class '{v}' does not match the pattern 'prefix-suffix'"
            ) from None

        if prefix not in ALLOWED_PREFIXES:
            raise ValueError(
                f"The storage_class prefix '{prefix}' does not match any of the supported supported prefixes:"
                f" [{', '.join(ALLOWED_PREFIXES)}]"
            )

        if prefix == "default":
            DefaultStorageClass(v)

        return v


class StorageMapMixin(PydanticBaseModel):
    storage: Dict[str, StorageConfiguration] = Field(
        default_factory=list,
        description="Mapping of storage locations (as URL) local to this level of the hierarchy",
    )

    @validator("storage")
    def storage_key(cls, v):  # noqa: B902
        """Verify that the storage key matches an URL, can be fully replaced by AnyURL with Pydantic 1.9"""
        for key in v:
            res = urlparse(key)
            if not res.scheme:
                raise ValueError(
                    f"Storage key '{key}' does not contain an URL protocol"
                )
        return v
