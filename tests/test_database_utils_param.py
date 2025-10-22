from __future__ import annotations

import importlib.util
import sys
from types import ModuleType


# Provide a lightweight dummy sqlalchemy package only if the real package is not importable
if importlib.util.find_spec("sqlalchemy") is None:
    # top-level package
    sqlalchemy = ModuleType("sqlalchemy")
    # minimal symbols expected by src.database.database_utils
    sqlalchemy.Engine = object
    sqlalchemy.text = lambda s: s

    # sqlalchemy.engine.create.event and create_engine
    engine_mod = ModuleType("sqlalchemy.engine")
    create_mod = ModuleType("sqlalchemy.engine.create")

    def dummy_listens_for(target, name):
        def _decorator(fn):
            return fn

        return _decorator

    create_mod.event = dummy_listens_for
    engine_mod.create = create_mod
    sqlalchemy.engine = engine_mod

    # dummy create_engine returns a simple sentinel object used by db_setup; tests
    # will not exercise real DB operations because Session is monkeypatched in tests
    def create_engine(url, echo=False):
        return object()

    sqlalchemy.create_engine = create_engine
    sys.modules["sqlalchemy.engine.create"] = create_mod

    # sqlalchemy.orm.Session placeholder (actual Session will be monkeypatched in tests)
    orm_mod = ModuleType("sqlalchemy.orm")
    orm_mod.Session = object
    sqlalchemy.orm = orm_mod

    # register submodules
    sys.modules["sqlalchemy"] = sqlalchemy
    sys.modules["sqlalchemy.engine"] = engine_mod
    sys.modules["sqlalchemy.engine.create"] = create_mod
    sys.modules["sqlalchemy.orm"] = orm_mod

import src.database.database_utils as dbu


def test_get_setting_none(monkeypatch):
    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, key):
            return None

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    assert dbu.get_setting("nope") is None


def test_format_get_birthdays_today(monkeypatch):
    # mock execute to return rows
    class DummyResult:
        def fetchall(self):
            return [(1, 12345, None)]

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, *args, **kwargs):
            return DummyResult()

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    res = dbu.get_birthdays_today()
    assert isinstance(res, list)
    assert res[0]["user_id"] == 12345
