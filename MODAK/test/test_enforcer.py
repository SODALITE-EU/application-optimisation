from sqlalchemy import insert

from MODAK import db
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


def test_enforce_infra_script(dbengine):
    """
    Check that Enforcer.enforce_opt returns an infra-conditioned script
    """

    driver = MODAK_driver(dbengine)
    enforcer = Enforcer(driver)

    stmt = insert(db.Script).values(
        conditions={"infrastructure": {"name": "testinfra"}},
        data={"stage": "pre", "raw": "echo hello"},
    )
    driver.updateSQL(stmt)

    scripts = enforcer.enforce_opt(
        "inexistentapp",
        Target(name="testinfra", job_scheduler_type="slurm"),
        [],
    )

    assert scripts, "empty list of scripts returned"
    assert scripts[0].conditions.infrastructure.name == "testinfra"

    scripts = enforcer.enforce_opt(
        "inexistentapp",
        Target(name="wrongtestinfra", job_scheduler_type="slurm"),
        [],
    )

    assert not scripts, "scripts returned while it should not have"


def test_enforce_app_script(dbengine):
    """
    Check that Enforcer.enforce_opt returns an app-conditioned script
    """

    driver = MODAK_driver(dbengine)
    enforcer = Enforcer(driver)

    stmt = insert(db.Script).values(
        conditions={"application": {"name": "fancy"}},
        data={"stage": "pre", "raw": "echo hello"},
    )
    driver.updateSQL(stmt)

    scripts = enforcer.enforce_opt(
        "inexistentapp",
        Target(name="testinfra", job_scheduler_type="slurm"),
        [],
    )

    assert not scripts, "scripts returned while it should not have"

    # despite target and myfeat, this should return the script
    scripts = enforcer.enforce_opt(
        "fancy",
        Target(name="testinfra", job_scheduler_type="slurm"),
        ["myfeat:true"],
    )

    assert scripts, "scripts not found"


def test_enforce_infra_storage_script(dbengine):
    """
    Check that Enforcer.enforce_opt returns an infra- & storage-conditioned script
    """

    driver = MODAK_driver(dbengine)
    enforcer = Enforcer(driver)

    # insert a script which should be enabled if the chosen infra provides this storage_class
    stmt = insert(db.Script).values(
        conditions={"infrastructure": {"name": "testinfra", "storage_class": "ssd"}},
        data={"stage": "pre", "raw": "echo hello"},
    )
    driver.updateSQL(stmt)

    scripts = enforcer.enforce_opt(
        "inexistentapp",
        Target(name="testinfra", job_scheduler_type="slurm"),
        [],
    )

    assert not scripts, "script returned despite no infrastructure entry"

    stmt = insert(db.Infrastructure).values(
        name="testinfra",
        configuration={"storage": {"file:///var/tmp": {"storage_class": "ssd"}}},
    )
    driver.updateSQL(stmt)

    scripts = enforcer.enforce_opt(
        "fancy",
        Target(name="testinfra", job_scheduler_type="slurm"),
        ["myfeat:true"],
    )

    assert scripts, "scripts not found"

    # insert a script which should be enabled if the chosen infra provides this storage_class
    stmt = insert(db.Script).values(
        conditions={
            "infrastructure": {"storage_class": "ssd"},
            "application": {"name": "testapp"},
        },
        data={"stage": "pre", "raw": "echo hello"},
    )
    driver.updateSQL(stmt)

    scripts = enforcer.enforce_opt(
        "testapp",
        Target(name="testinfra", job_scheduler_type="slurm"),
        [],
    )
    assert len(scripts) == 2, "scripts not found"
