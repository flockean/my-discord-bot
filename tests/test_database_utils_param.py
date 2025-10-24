from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import String
import src.database.database_utils as dbu


class DummyModel(dbu.Base):
    __tablename__ = "dummy"
    id = Column(String, primary_key=True)
    field = Column(String)
    date_field = Column(String)

    def __init__(self, id="test1", field="value", date_field=None):
        self.id = id
        self.field = field
        self.date_field = date_field


def test_get_by_id(monkeypatch):
    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, model, id):
            if id == "exists":
                return DummyModel()
            return None

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    assert dbu.get_by_id(DummyModel, "exists") is not None
    assert dbu.get_by_id(DummyModel, "missing") is None


def test_get_by_filter(monkeypatch):
    class DummyExecute:
        def scalars(self):
            return self

        def all(self):
            return [DummyModel()]

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, query):
            return DummyExecute()

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    results = dbu.get_by_filter(DummyModel, field="value")
    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], DummyModel)


def test_query_by_date_parts(monkeypatch):
    class DummyExecute:
        def scalars(self):
            return self

        def all(self):
            return [DummyModel()]

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, query):
            return DummyExecute()

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    results = dbu.query_by_date_parts(DummyModel, "date_field", 10, 24)
    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], DummyModel)
