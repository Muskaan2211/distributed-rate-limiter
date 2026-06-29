from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_root_points_to_dashboard_and_docs():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    body = response.json()
    assert body['dashboard'] == '/dashboard'
    assert body['docs'] == '/docs'
