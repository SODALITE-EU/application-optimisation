from MODAK.enforcer import Enforcer
from MODAK.MODAK_driver import MODAK_driver
from MODAK.model import Target


def test_enforce_opt():
    """
    Check that Enforcer.enforce_opt returns a non-empty set of and location for a DB entry
    """

    driver = MODAK_driver()
    enforcer = Enforcer(driver)
    scripts = enforcer.enforce_opt(
        "tensorflow",
        Target(name="test", job_scheduler_type="slurm"),
        ["version:2.1", "xla:true"],
    )

    assert scripts, "empty set returned"
