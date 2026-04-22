from fastapi.testclient import TestClient

from app.main import app


def _auth_headers(client: TestClient, username: str, password: str):
    register_payload = {"username": username, "password": password}
    client.post("/auth/register", json=register_payload)

    token_response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_requires_auth_for_tasks():
    with TestClient(app) as client:
        response = client.get("/tasks/")
        assert response.status_code == 401


def test_task_crud_flow():
    with TestClient(app) as client:
        headers = _auth_headers(client, "alice", "password123")

        create_response = client.post(
            "/tasks/",
            json={"title": "Write tests", "description": "Cover auth + CRUD"},
            headers=headers,
        )
        assert create_response.status_code == 200
        created_task = create_response.json()
        task_id = created_task["id"]

        list_response = client.get("/tasks/", headers=headers)
        assert list_response.status_code == 200
        assert any(task["id"] == task_id for task in list_response.json())

        update_response = client.put(
            f"/tasks/{task_id}",
            json={"completed": True},
            headers=headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True

        delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
        assert delete_response.status_code == 200

        missing_response = client.get(f"/tasks/{task_id}", headers=headers)
        assert missing_response.status_code == 404


def test_task_ownership_isolation():
    with TestClient(app) as client:
        alice_headers = _auth_headers(client, "alice2", "password123")
        bob_headers = _auth_headers(client, "bob2", "password123")

        create_response = client.post(
            "/tasks/",
            json={"title": "Alice private task", "description": "owned by alice"},
            headers=alice_headers,
        )
        task_id = create_response.json()["id"]

        bob_read = client.get(f"/tasks/{task_id}", headers=bob_headers)
        assert bob_read.status_code == 404

        bob_delete = client.delete(f"/tasks/{task_id}", headers=bob_headers)
        assert bob_delete.status_code == 404


def test_filter_and_sort_tasks():
    with TestClient(app) as client:
        headers = _auth_headers(client, "carol", "password123")

        client.post("/tasks/", json={"title": "B task", "description": "open"}, headers=headers)
        client.post("/tasks/", json={"title": "A task", "description": "done"}, headers=headers)

        all_tasks = client.get("/tasks/?sort=title", headers=headers)
        assert all_tasks.status_code == 200
        titles = [task["title"] for task in all_tasks.json()]
        assert titles == sorted(titles)

        first_task_id = all_tasks.json()[0]["id"]
        complete_response = client.put(
            f"/tasks/{first_task_id}",
            json={"completed": True},
            headers=headers,
        )
        assert complete_response.status_code == 200

        completed_only = client.get("/tasks/?completed=true", headers=headers)
        assert completed_only.status_code == 200
        assert all(task["completed"] is True for task in completed_only.json())

        invalid_sort = client.get("/tasks/?sort=bad_field", headers=headers)
        assert invalid_sort.status_code == 400
