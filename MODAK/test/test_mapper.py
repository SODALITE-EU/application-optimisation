import json
import pathlib
import unittest
from unittest.mock import patch

from sqlalchemy import delete, insert, select

from MODAK.db import Map, Optimisation
from MODAK.mapper import Mapper
from MODAK.MODAK_driver import MODAK_driver
from MODAK.model import JobModel
from MODAK.settings import Settings

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


class test_mapper(unittest.TestCase):
    def setUp(self):
        self.driver = MODAK_driver()
        self.m = Mapper(self.driver)

    def tearDown(self):
        pass

    def test_add_opt(self):
        target_string = '{"cpu_type":"x86","acc_type":"nvidia"}'
        opt_string = '{"xla":true,"version":"1.1"}'

        stmt = delete(Optimisation).where(
            Optimisation.opt_dsl_code == "TF_PIP_XLA"
        )  # no need to delete Mapper, since DB is set to CASCADE
        self.driver.updateSQL(stmt)
        self.m.add_optimisation(
            "TF_PIP_XLA",
            "tensorflow",
            json.loads(target_string),
            json.loads(opt_string),
        )
        data = self.driver.selectSQL(
            select(Optimisation.app_name).where(
                Optimisation.opt_dsl_code == "TF_PIP_XLA"
            )
        )
        self.assertEqual(len(data), 1)
        print(data[0][0])
        self.assertEqual(data[0][0], "tensorflow")

    def test_add_container(self):
        stmt = delete(Map).where(Map.opt_dsl_code == "TF_PIP_XLA")
        self.driver.updateSQL(stmt)
        data = self.driver.selectSQL(
            select(Map.container_file).where(Map.opt_dsl_code == "TF_PIP_XLA")
        )
        self.assertEqual(len(data), 0)
        self.m.add_container(
            "TF_PIP_XLA", "AI/containers/tensorflow/tensorflow_pip_xla"
        )
        data = self.driver.selectSQL(
            select(Map.container_file).where(Map.opt_dsl_code == "TF_PIP_XLA")
        )
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][0], "AI/containers/tensorflow/tensorflow_pip_xla")

    def test_map_container_ai(self):
        dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"

        model = JobModel.parse_raw(dsl_file.read_text())
        new_container = self.m.map_container(
            model.job.application, model.job.optimisation
        )
        self.assertEqual(
            new_container, "docker.io://modakopt/modak:tensorflow-2.1-gpu-src"
        )

    def test_map_container_hpc(self):
        model = JobModel.parse_raw(
            SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text()
        )
        assert model.job.optimisation

        dsl_code = self.m._decode_hpc_opt(
            model.job.application.app_tag, model.job.optimisation
        )
        self.assertEqual(dsl_code, "mpich_ub1804_cuda101_mpi314_gnugprof")

    def test_map_container_aliased(self):
        dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"

        with patch.object(Settings, "image_hub_aliases", {"docker": "docker.invalid"}):
            model = JobModel.parse_raw(dsl_file.read_text())
            new_container = self.m.map_container(
                model.job.application, model.job.optimisation
            )
            self.assertEqual(
                new_container,
                "docker.invalid://modakopt/modak:tensorflow-2.1-gpu-src",
            )


def test_non_app_tag_mapping(modak_driver):
    mapper = Mapper(modak_driver)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich",
        app_name="mpich",
        target="enable_opt_build:true,cpu_type:x86,acc_type:nvidia,",
        optimisation="version:3.1.4|",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich",
        container_file="nvidia_mpich",
        image_type="shub",
        image_hub="library",
    )
    modak_driver.updateSQL(optstmt)
    modak_driver.updateSQL(mapstmt)

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    assert mapper._decode_hpc_opt(model.job.application.app_tag, model.job.optimisation)
    assert mapper.map_container(model.job.application, model.job.optimisation)


def test_app_tag_mapping_missing(modak_driver):
    mapper = Mapper(modak_driver)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich",
        app_name="mpich",
        target="enable_opt_build:true,cpu_type:x86,acc_type:nvidia,",
        optimisation="version:3.1.4|",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich",
        container_file="nvidia_mpich",
        image_type="shub",
        image_hub="library",
    )
    modak_driver.updateSQL(optstmt)
    modak_driver.updateSQL(mapstmt)

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    model.job.application.app_tag = "code_aster"

    assert not mapper._decode_hpc_opt(
        model.job.application.app_tag, model.job.optimisation
    )
    assert not mapper.map_container(model.job.application, model.job.optimisation)


def test_app_tag_mapping(modak_driver):
    mapper = Mapper(modak_driver)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich",
        app_name="mpich",
        target="enable_opt_build:true,cpu_type:x86,acc_type:nvidia,",
        optimisation="version:3.1.4|",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich",
        container_file="nvidia_mpich",
        image_type="shub",
        image_hub="library",
    )
    modak_driver.updateSQL(optstmt)
    modak_driver.updateSQL(mapstmt)

    optstmt = insert(Optimisation).values(
        opt_dsl_code="nvidia-mpich-code_aster",
        app_name="code_aster",
        target="enable_opt_build:false,cpu_type:x86,acc_type:nvidia",
        optimisation="version:3.1.4|library:mpich",
        version="3.1.4",
    )
    mapstmt = insert(Map).values(
        opt_dsl_code="nvidia-mpich-code_aster",
        container_file="nvidia_mpich-code_aster_avx2",
        image_type="shub",
        image_hub="library",
    )
    modak_driver.updateSQL(optstmt)
    modak_driver.updateSQL(mapstmt)

    model = JobModel.parse_raw(SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text())
    model.job.application.app_tag = "code_aster"
    model.job.optimisation.enable_opt_build = (
        False  # there is not much in requesting an optimization build now
    )

    dsl_code = mapper._decode_hpc_opt(
        model.job.application.app_tag, model.job.optimisation
    )
    assert dsl_code
    assert dsl_code == "nvidia-mpich-code_aster"
    assert mapper.map_container(model.job.application, model.job.optimisation)
