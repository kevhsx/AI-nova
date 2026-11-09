import pytest
from fastapi import HTTPException

import main


def test_health_and_home(client):
    assert client.get('/health').json()['status'] == 'ok'
    assert 'text/html' in client.get('/').headers['content-type']


def test_session_lifecycle(client, headers):
    assert client.get('/auth/me', headers=headers).json()['user']['username'] == 'test_user'
    assert client.post('/auth/logout', headers=headers).status_code == 200
    assert client.get('/auth/me', headers=headers).status_code == 401


def test_duplicate_registration(client, headers):
    response = client.post('/auth/register', json={
        'username': 'test_user', 'password': 'Testing123', 'display_name': 'Duplicate'})
    assert response.status_code == 409


@pytest.mark.parametrize('username,password', [('ab', 'Testing123'), ('valid_user', 'short'),
                                               ('valid_user', 'abcdefgh')])
def test_invalid_registration(client, username, password):
    assert client.post('/auth/register', json={
        'username': username, 'password': password, 'display_name': 'Test'}).status_code == 400


def test_login_password_and_role_boundaries(client, headers):
    assert client.post('/auth/login', json={
        'username': 'test_user', 'password': 'Wrong123'}).status_code == 401
    response = client.post('/auth/login', json={
        'username': 'test_user', 'password': 'Testing123'})
    assert response.status_code == 200
    assert client.get('/admin/users', headers=headers).status_code == 403
    assert client.get('/admin/logs', headers=headers).status_code == 403


@pytest.mark.parametrize('endpoint,payload', [('/resume', {'text': 'Experience'}),
    ('/translate', {'text': 'Hello'}), ('/copywrite', {'scene': 'A product'})])
def test_text_features_require_authentication_and_log_success(client, headers, endpoint, payload):
    assert client.post(endpoint, json=payload).status_code == 401
    response = client.post(endpoint, json=payload, headers=headers)
    assert response.status_code == 200
    assert 'SIMULATED RESPONSE' in response.text
    with main.get_db() as db:
        log = db.execute('SELECT * FROM activity_logs').fetchone()
        assert log['status'] == 'success'
        assert log['user_id'] > 0


def test_provider_failure_is_logged(client, headers, monkeypatch):
    def fail(prompt, provider):
        raise HTTPException(status_code=503, detail='Simulated provider failure')
    monkeypatch.setattr(main, 'call_llm', fail)
    assert client.post('/resume', json={'text': 'Example'}, headers=headers).status_code == 503
    with main.get_db() as db:
        assert db.execute('SELECT status FROM activity_logs').fetchone()['status'] == 'error'


@pytest.mark.parametrize('endpoint,filename,content', [
    ('/pdf-summary', 'wrong.txt', b'text'), ('/pdf-summary', 'broken.pdf', b'not a PDF'),
    ('/csv-preview', 'empty.csv', b''), ('/csv-preview', 'wrong.txt', b'a,b')])
def test_invalid_uploads(client, headers, endpoint, filename, content):
    assert client.post(endpoint, headers=headers,
        files={'file': (filename, content)}).status_code == 400


def test_csv_preview(client, headers):
    response = client.post('/csv-preview', headers=headers,
        files={'file': ('sample.csv', b'name,value\na,1\nb,2')})
    assert response.status_code == 200
    with main.get_db() as db:
        assert db.execute('SELECT feature FROM activity_logs').fetchone()['feature'] == 'csv_preview'
