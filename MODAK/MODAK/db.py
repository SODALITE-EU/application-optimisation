__all__ = ["Optimisation", "Map", "OptScript"]

from sqlalchemy import Column, ForeignKey, Integer, String, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()


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


class OptScript(Base):
    __tablename__ = "optscript"

    opt_code = Column(String(255), primary_key=True)
    script_name = Column(String(255), nullable=False)
    script_loc = Column(String(5000), nullable=True)
    stage = Column(Integer, nullable=True)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Always enable foreign key support on SQLite
    see https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
