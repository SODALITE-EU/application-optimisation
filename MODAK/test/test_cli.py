def test_modak(script_runner):
    ret = script_runner.run(
        "modak", "-i", "test/input/mpi_test.json", "-o", "/dev/null"
    )
    assert ret.success
