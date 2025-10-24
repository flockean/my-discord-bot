from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import String
from src.database import database_utils as dbu
from src.models.schemas import Base

import pytest


class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(String, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"<TestModel(id={self.id}, name={self.name})>"


@pytest.fixture
def test_model():
    model = TestModel()
    model.id = "test1"
    model.name = "Test"
    return model


def test_add(monkeypatch, test_model):
    added_model = None
    committed = False
    refreshed = False

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def add(self, model):
            nonlocal added_model
            added_model = model

        def commit(self):
            # Simulate DB commit
            nonlocal committed
            committed = True

        def refresh(self, model):
            # Simulate DB refresh
            nonlocal refreshed
            refreshed = True

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    dbu.add(test_model)
    assert added_model == test_model  # Compare equality, not identity
    assert committed
    assert refreshed


def test_delete_existing(monkeypatch):
    deleted_model = None
    committed = False

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, model_class, id):
            return TestModel(id=id)

        def delete(self, model):
            nonlocal deleted_model
            deleted_model = model

        def commit(self):
            # Simulate DB commit
            nonlocal committed
            committed = True

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    dbu.delete(TestModel, "test1")
    assert deleted_model  # Check that we have a model
    assert deleted_model.id == "test1"
    assert committed


def test_delete_nonexistent(monkeypatch):
    committed = False

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, model_class, id):
            return None

        def delete(self, model):
            pytest.fail("Should not try to delete non-existent model")

        def commit(self):
            # Simulate DB commit
            nonlocal committed
            committed = True

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    dbu.delete(TestModel, "missing")  # Should not raise exception
    assert not committed


def test_update_by_id(monkeypatch):
    updated = False
    test_model = TestModel()

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, model_class, id):
            return test_model

        def commit(self):
            # Simulate DB commit
            nonlocal updated
            updated = True

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    result = dbu.update_by_id(TestModel, "test1", name="New Name")
    assert result == True
    assert updated
    assert test_model.name == "New Name"


def test_update_nonexistent(monkeypatch):
    committed = False

    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, model_class, id):
            return None

        def commit(self):
            # Simulate DB commit
            nonlocal committed
            committed = True
            pytest.fail("Should not commit when model doesn't exist")

    monkeypatch.setattr(dbu, "Session", lambda bind=None: DummySession())
    result = dbu.update_by_id(TestModel, "missing", name="New Name")
    assert result == False
    assert not committed
