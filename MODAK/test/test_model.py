import pytest
from pydantic import ValidationError

from MODAK.model.cpu import CPU
from MODAK.model.storage import StorageMapMixin


def test_cpu():
    cpu = CPU(arch="arm", ncores=4)
    assert cpu.arch == "arm"

    cpu = CPU(arch="x86_64", microarch="zen", ncores=64)
    assert cpu.arch == "x86_64" and cpu.microarch == "zen"

    cpu = CPU(arch="aarch64", microarch="m1", ncores=8)
    assert cpu.arch == "aarch64" and cpu.microarch == "m1"

    with pytest.raises(ValidationError) as exc:
        CPU(arch="aarch64", microarch="zen", ncores=64)
        assert "invalid microarchitecture" in str(exc)


def test_storage_map():
    mixin = StorageMapMixin(
        storage={"file:///var/tmp": {"storage_class": "default-ssd"}}
    )
    assert mixin

    with pytest.raises(ValidationError) as exc:
        StorageMapMixin(storage={"foo": {"storage_class": "default-ssd"}})
        assert "not an URL" in str(exc)
