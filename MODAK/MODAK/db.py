__all__ = ["Optimisation", "Map", "Infrastructure", "Script"]

import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


Base = declarative_base()


class Optimisation(Base):
    __tablename__ = "optimisation"

    opt_dsl_code = Column(String(255), primary_key=True)
    app_name = Column(String(255), nullable=False)
    target = Column(String(5000), nullable=True, default=None)
    optimisation = Column(String(5000), nullable=True)
    version = Column(String(255), nullable=True)


class Map(Base):
    __tablename__ = "mapper"

    map_id = Column(Integer, primary_key=True)
    opt_dsl_code = Column(
        String(255),
        ForeignKey("optimisation.opt_dsl_code", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    container_file = Column(String(255), nullable=True, default=None)
    image_type = Column(String(255), nullable=True, default=None)
    image_hub = Column(String(255), nullable=True, default=None)
    src = Column(String(255), nullable=True, default=None)


class ScalingModel(Base):
    __tablename__ = "scaling_model"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    opt_dsl_code = Column(
        String(255),
        ForeignKey("optimisation.opt_dsl_code", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    model = Column(JSON, nullable=False)


class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), primary_key=True, unique=True)  # for now unique
    disabled = Column(
        DateTime, nullable=True
    )  # use a timestamp to get more information on when it was disabled
    description = Column(Text, nullable=True)
    configuration = Column(JSON, nullable=False, server_default="{}")


class Script(Base):
    """Infrastructure- or code-specific environment setup and teardown scripts.

    An infrastructures or a code may need additional settings (environment variables,
    modules loaded, etc.) to run specific workloads. We allow for schema-less conditions
    (which will be tied to an infrastructures configuration or code-specific features
    and will be evaluated against the requested/required capabilities of a workload) and
    store them in another schema-less column.

    Examples for conditions (in YAML):

    1) to always include this when running on the hlrs_testbed infrastructure

        infrastructure:
            name: hlrs_testbed

    2) to always include this when running on the specified infras GPU partition

        infrastructure:
            id: F1069039-492D-4A23-BFB1-03AECC593C64
            partition: gpu

    2) or alternatively, when requesting GPU acceleration on the same infrastructure

        infrastructure:
            id: F1069039-492D-4A23-BFB1-03AECC593C64
            accelerator: gpu

    3) to be included when running a tensorflow workflow with the XLA compiler enabled

        application:
            name: tensorflow
            feature: xla

    Examples for data (in YAML):

    1) a string which will be inserted verbatim into the generated script right after
       the generated headers

        stage: pre
        raw: "export FOO=bar\\\nmodule load baz"

    2) the same input, but structured (which would allow to yield code for different
       shells or module environments):

        stage: pre
        structure:
        - env:
            FOO: bar
        - module:
            load: baz

    3) to include a script which has to be run by a different interpreter:

        stage: pre
        interpreter: #!/usr/bin/env python
        raw: "print('hello, world!')"
    """

    __tablename__ = "script"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=True)
    conditions = Column(JSON, nullable=False, server_default="{}")
    data = Column(JSON, nullable=False, server_default="{}")


@listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Always enable foreign key support on SQLite
    see https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
