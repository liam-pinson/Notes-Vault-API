from fastapi.testclient import TestClient

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "securepass123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert "hashed_password" not in response.json()

def test_register_duplicate_user(client):
    client.post("/auth/register", json={
        "username": "dupeuser",
        "password": "securepass123"
    })
    response = client.post("/auth/register", json={
        "username": "dupeuser",
        "password": "securepass123"
    })
    assert response.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "securepass123"
    })
    response = client.post("/auth/token", data={
        "username": "loginuser",
        "password": "securepass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "securepass123"
    })
    response = client.post("/auth/token", data={
        "username": "loginuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_create_note(authenticated_client):
    response = authenticated_client.post("/notes/", json={
        "title": "Test Note",
        "content": "This is my test note content"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Note"
    assert response.json()["content"] == "This is my test note content"
    assert "id" in response.json()
    assert "created_at" in response.json()

def test_create_note_empty_content(authenticated_client):
    response = authenticated_client.post("/notes/", json={
        "content": ""
    })
    assert response.status_code == 422

def test_create_note_unauthenticated(client):
    response = client.post("/notes/", json={
        "content": "This should fail"
    })
    assert response.status_code == 401

def test_list_notes(authenticated_client):
    authenticated_client.post("/notes/", json={"content": "Note one"})
    authenticated_client.post("/notes/", json={"content": "Note two"})
    response = authenticated_client.get("/notes/")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["notes"]) == 2

def test_list_notes_search(authenticated_client):
    authenticated_client.post("/notes/", json={"content": "Buy milk"})
    authenticated_client.post("/notes/", json={"content": "Call the doctor"})
    response = authenticated_client.get("/notes/?search=milk")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["notes"][0]["content"] == "Buy milk"

def test_get_note_by_id(authenticated_client):
    create_response = authenticated_client.post("/notes/", json={
        "content": "Find me by ID"
    })
    note_id = create_response.json()["id"]
    response = authenticated_client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id

def test_get_note_not_found(authenticated_client):
    response = authenticated_client.get("/notes/nonexistent-id")
    assert response.status_code == 404

def test_update_note(authenticated_client):
    create_response = authenticated_client.post("/notes/", json={
        "content": "Original content"
    })
    note_id = create_response.json()["id"]
    response = authenticated_client.patch(f"/notes/{note_id}", json={
        "content": "Updated content"
    })
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"

def test_delete_note(authenticated_client):
    create_response = authenticated_client.post("/notes/", json={
        "content": "Delete me"
    })
    note_id = create_response.json()["id"]
    delete_response = authenticated_client.delete(f"/notes/{note_id}")
    assert delete_response.status_code == 204
    get_response = authenticated_client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404

def test_cannot_access_other_users_note(client):
    client.post("/auth/register", json={
        "username": "user1",
        "password": "password123"
    })
    token_response = client.post("/auth/token", data={
        "username": "user1",
        "password": "password123"
    })
    user1_token = token_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    note_response = client.post("/notes/", json={"content": "User1 private note"})
    note_id = note_response.json()["id"]

    client.post("/auth/register", json={
        "username": "user2",
        "password": "password123"
    })
    token_response = client.post("/auth/token", data={
        "username": "user2",
        "password": "password123"
    })
    user2_token = token_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {user2_token}"})
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 404