def test_simple_example(script_runner):
    ret = script_runner.run("examples/example.py")
    assert ret.success
