import asyncio

import rethinkdb as r

import pytest
import aiorethink
from aiorethink.registry import registry


@pytest.fixture(scope = "session")
def _db_config():
    # configure DB exactly once
    aiorethink.configure_db_connection(db = "testing")
    return None


@pytest.yield_fixture
def db_conn(_db_config, event_loop):
    yield aiorethink.db_conn

    event_loop.run_until_complete(
            aiorethink.db_conn.close(False)
            )


@pytest.yield_fixture
def aiorethink_session(db_conn):
    yield None
    registry.clear()


@pytest.yield_fixture
def aiorethink_db_session(db_conn, event_loop):
    arun = event_loop.run_until_complete
    cn = arun(db_conn.get())

    dbs = arun(r.db_list().run(cn))
    if "testing" in dbs:
        raise RuntimeError("There is already a database named 'testing'.")

    arun(r.db_create("testing").run(cn))

    yield None

    arun(r.db_drop("testing").run(cn))
    registry.clear()