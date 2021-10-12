from MODAK.enforcer import Enforcer
from MODAK.MODAK_driver import MODAK_driver


def test_enforce_opt():
    """
    Check that Enforcer.enforce_opt returns a non-empty set of and location for a DB entry
    """

    driver = MODAK_driver()
    enforcer = Enforcer(driver)
    opts = enforcer.enforce_opt(["version:2.1", "xla:true"])

    assert opts, "empty set returned"
    for opt in opts:
        assert opt.script_name, "script_name empty while it shouldn't be"
        assert opt.script_loc, "script_loc empty while it shouldn't be"
