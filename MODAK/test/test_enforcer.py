from MODAK.enforcer import Enforcer
from MODAK.MODAK_driver import MODAK_driver


def test_enforce_opt():
    """
    Check that Enforcer.enforce_opt returns a non-empty set of and location for a DB entry
    """

    driver = MODAK_driver()
    enforcer = Enforcer(driver)
    opts = ["version:2.1", "xla:true"]
    dfs = enforcer.enforce_opt(opts)

    assert dfs, "empty set returned"
    for df in dfs:
        for idx in range(0, df.shape[0]):
            assert df["script_name"][idx], "script_name empty while it shouldn't be"
            assert df["script_loc"][idx], "script_loc empty while it shouldn't be"
