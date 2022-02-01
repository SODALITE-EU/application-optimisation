def test_modak(script_runner):
    ret = script_runner.run(
        "modak", "-i", "test/input/mpi_test.json", "-o", "/dev/null"
    )
    assert ret.success


def test_validate_json(script_runner):
    ret = script_runner.run("modak-validate-json", "test/input/mpi_test_egi.json")
    assert ret.success
    assert "OK: Validation succeeded." in ret.stderr


def test_import_script(script_runner):
    ret = script_runner.run(
        "modak-import-script",
        "--stage",
        "pre",
        "--condition-application-name",
        "pytorch",
        "--condition-application-feature",
        "cuda=True",
        "test/input/script_load_cudatoolkit.sh",
    )
    assert ret.success
    assert "Feature" in ret.stdout


def test_import_script_non_existent_infra(script_runner):
    """Adding a script for a non-existent infra should fail"""
    ret = script_runner.run(
        "modak-import-script",
        "--condition-infrastructure-name",
        "non-existent",
        "test/input/script_load_cudatoolkit.sh",
    )
    assert not ret.success
    assert "No infrastructure found" in ret.stderr


def test_schema_sql(script_runner):
    ret = script_runner.run("modak-schema", "sql")
    assert ret.success
    assert ret.stdout


def test_schema_openapi(script_runner):
    ret = script_runner.run("modak-schema", "openapi")
    assert ret.success
    assert ret.stdout


def test_schema_dsl(script_runner):
    ret = script_runner.run("modak-schema", "dsl")
    assert ret.success
    assert ret.stdout
