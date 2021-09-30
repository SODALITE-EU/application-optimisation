def test_modak_cli(script_runner):
    ret = script_runner.run(
        "examples/modak.py", "-i", "test/input/mpi_test.json", "-o", "/dev/null"
    )
    assert ret.success


def test_simple_example(script_runner):
    ret = script_runner.run("examples/example.py")
    assert ret.success
