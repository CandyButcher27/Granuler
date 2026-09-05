"""The single-user gate in front of every route except /health."""
import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


def _client(monkeypatch, user, password):
    monkeypatch.setenv("GRANULER_USER", user)
    monkeypatch.setenv("GRANULER_PASSWORD", password)
    import api.main

    return TestClient(importlib.reload(api.main).app)


@pytest.fixture(autouse=True)
def _restore_module():
    yield
    import api.main

    importlib.reload(api.main)


def test_health_needs_no_credentials(monkeypatch):
    assert _client(monkeypatch, "ravi", "s3cret").get("/health").status_code == 200


def test_the_tool_itself_is_not_public(monkeypatch):
    response = _client(monkeypatch, "ravi", "s3cret").get("/")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"].startswith("Basic")


def test_the_configured_user_gets_in(monkeypatch):
    assert _client(monkeypatch, "ravi", "s3cret").get("/", auth=("ravi", "s3cret")).status_code == 200


@pytest.mark.parametrize("attempt", [("ravi", "wrong"), ("someone", "s3cret"), ("", "")])
def test_wrong_credentials_are_rejected(monkeypatch, attempt):
    assert _client(monkeypatch, "ravi", "s3cret").get("/", auth=attempt).status_code == 401


def test_an_unconfigured_deploy_serves_nobody(monkeypatch):
    """Fail closed. A missing password must never mean "let everyone in"."""
    response = _client(monkeypatch, "", "").get("/", auth=("ravi", "s3cret"))
    assert response.status_code == 503
