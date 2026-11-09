import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Import the real application without loading a developer's local credentials.
os.environ['PYTHON_DOTENV_DISABLED'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DB_PATH', tmp_path / 'test.db')
    monkeypatch.setattr(main, 'call_llm', lambda prompt, provider: 'SIMULATED RESPONSE')
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def headers(client):
    response = client.post('/auth/register', json={
        'username': 'test_user', 'password': 'Testing123', 'display_name': 'Test User'})
    assert response.status_code == 201
    return {'X-Session-Token': response.json()['token']}
