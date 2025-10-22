from __future__ import annotations

import sys
from types import ModuleType

import pytest


# Provide dummy requests if not installed so module import won't fail during test collection
if "requests" not in sys.modules:
    sys.modules["requests"] = ModuleType("requests")

import src.service.api as api


def test_get_api_returns_json(monkeypatch):
    class DummyResp:
        status_code = 200

        def json(self):
            return {"ok": True}

    import sys

    requests_mod = sys.modules.get("requests")
    monkeypatch.setattr(requests_mod, "get", lambda url: DummyResp(), raising=False)
    assert api.get_api("http://example") == {"ok": True}


@pytest.mark.parametrize("emote,expected_key", [("cat", "url"), ("fox", "url")])
def test_neko_best_parses_results(monkeypatch, emote, expected_key):
    monkeypatch.setattr(
        "src.service.api.get_api",
        lambda url: {"results": [{expected_key: "https://img.example/1.png"}]},
    )
    res = api.neko_best(emote)
    assert res.endswith(".png")
