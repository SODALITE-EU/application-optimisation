from sqlalchemy import insert

from MODAK import db
from MODAK.driver import Driver
from MODAK.enforcer import Enforcer
from MODAK.model import Application, Job, ScriptIn, Target
from MODAK.model.infrastructure import InfrastructureIn


def test_enforce_opt():
    """
    Check that Enforcer.enforce_opt returns a non-empty set of and location for a DB entry
    """

    driver = Driver()
    enforcer = Enforcer(driver)
    scripts, _ = enforcer.enforce_opt(
        "tensorflow",
        Job.construct(target=Target(name="test", job_scheduler_type="slurm")),
        ["version:2.1", "xla:true"],
    )

    assert scripts, "empty set returned"


def test_enforce_infra_script(dbengine):
    """
    Check that Enforcer.enforce_opt returns an infra-conditioned script
    """

    driver = Driver(dbengine)
    enforcer = Enforcer(driver)

    stmt = insert(db.Script).values(
        conditions={"infrastructure": {"name": "testinfra"}},
        data={"stage": "pre", "raw": "echo hello"},
    )
    driver.update_sql(stmt)

    scripts, _ = enforcer.enforce_opt(
        "inexistentapp",
        Job.construct(target=Target(name="testinfra", job_scheduler_type="slurm")),
        [],
    )

    assert scripts, "empty list of scripts returned"
    assert scripts[0].conditions.infrastructure
    assert scripts[0].conditions.infrastructure.name == "testinfra"

    scripts, _ = enforcer.enforce_opt(
        "inexistentapp",
        Job.construct(target=Target(name="wrongtestinfra", job_scheduler_type="slurm")),
        [],
    )

    assert not scripts, "scripts returned while it should not have"


def test_enforce_app_script(dbengine):
    """
    Check that Enforcer.enforce_opt returns an app-conditioned script
    """

    driver = Driver(dbengine)
    enforcer = Enforcer(driver)

    script = ScriptIn(
        conditions={"application": {"name": "fancy"}},
        data={"stage": "pre", "raw": "echo hello"},
    )
    stmt = insert(db.Script).values(**script.dict())
    driver.update_sql(stmt)

    scripts, _ = enforcer.enforce_opt(
        "inexistentapp",
        Job.construct(target=Target(name="testinfra", job_scheduler_type="slurm")),
        [],
    )

    assert not scripts, "scripts returned while it should not have"

    # despite target and myfeat, this should return the script
    scripts, _ = enforcer.enforce_opt(
        "fancy",
        Job.construct(target=Target(name="testinfra", job_scheduler_type="slurm")),
        ["myfeat:true"],
    )

    assert scripts, "scripts not found"


def test_enforce_infra_storage_script(dbengine):
    """
    Check that Enforcer.enforce_opt returns an infra- & storage-conditioned script
    """

    driver = Driver(dbengine)
    enforcer = Enforcer(driver)

    # insert a script which should be enabled if the chosen infra provides this storage_class

    script = ScriptIn(
        conditions={
            "infrastructure": {"name": "testinfra", "storage_class": "default-ssd"}
        },
        data={"stage": "pre", "raw": "echo 'hello any storage'"},
    )
    stmt = insert(db.Script).values(**script.dict())
    driver.update_sql(stmt)

    scripts, _ = enforcer.enforce_opt(
        "inexistentapp",
        Job.construct(target=Target(name="testinfra", job_scheduler_type="slurm")),
        [],
    )

    assert not scripts, "script returned despite no infrastructure entry"

    infra = InfrastructureIn(
        name="testinfra",
        configuration={
            "storage": {"file:///var/tmp": {"storage_class": "default-ssd"}}
        },
    )
    stmt = insert(db.Infrastructure).values(**infra.dict())
    driver.update_sql(stmt)

    scripts, _ = enforcer.enforce_opt(
        "fancy",
        Job.construct(
            target=Target(name="testinfra", job_scheduler_type="slurm"),
            application=Application.construct(storage_class_pref=None),
        ),
        ["myfeat:true"],
    )

    assert scripts, "scripts not found"

    # insert a script which should be enabled if the chosen infra provides this storage_class
    script = ScriptIn(
        conditions={
            "infrastructure": {"storage_class": "default-ssd"},
            "application": {"name": "testapp"},
        },
        data={"stage": "pre", "raw": "echo 'hello ssd-only'"},
    )
    stmt = insert(db.Script).values(**script.dict())
    driver.update_sql(stmt)

    scripts, _ = enforcer.enforce_opt(
        "testapp",
        Job.construct(
            target=Target(name="testinfra", job_scheduler_type="slurm"),
            application=Application.construct(storage_class_pref=None),
        ),
        [],
    )
    assert len(scripts) == 2, "scripts not found"


def test_enforce_infra_storage_pref(dbengine):
    """
    Check that Enforcer.enforce_opt returns the storage location from an infra
    """

    driver = Driver(dbengine)
    enforcer = Enforcer(driver)

    infra = InfrastructureIn(
        name="testinfra",
        configuration={
            "storage": {
                "file:///var/tmp": {"storage_class": "default-ssd"},
                "file:///data": {"storage_class": "default-common"},
            }
        },
    )
    stmt = insert(db.Infrastructure).values(**infra.dict())
    driver.update_sql(stmt)

    _, tenv = enforcer.enforce_opt(
        "fancy",
        Job.construct(
            target=Target(name="testinfra", job_scheduler_type="slurm"),
            application=Application.construct(storage_class_pref=None),
        ),
        ["myfeat:true"],
    )

    # no spec will return the "slowest" (cheaptest) storage class first
    assert tenv["preferred_storage_location"] == "file:///data"

    _, tenv = enforcer.enforce_opt(
        "fancy",
        Job.construct(
            target=Target(name="testinfra", job_scheduler_type="slurm"),
            application=Application.construct(storage_class_pref="default-ssd"),
        ),
        ["myfeat:true"],
    )

    assert tenv["preferred_storage_location"] == "file:///var/tmp"
