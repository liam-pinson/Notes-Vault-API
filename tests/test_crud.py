from app import crud, schemas

def test_create_user(db):
    user = crud.create_user(db, schemas.UserCreate(
        username="cruduser",
        password="securepass123"
    ))
    assert user.username == "cruduser"
    assert user.hashed_password != "securepass123"
    assert user.id is not None

def test_password_hashing():
    hashed = crud.hash_password("mypassword")
    assert hashed != "mypassword"
    assert crud.verify_password("mypassword", hashed) is True
    assert crud.verify_password("wrongpassword", hashed) is False

def test_get_user_by_username(db):
    crud.create_user(db, schemas.UserCreate(
        username="findme",
        password="securepass123"
    ))
    user = crud.get_user_by_username(db, "findme")
    assert user is not None
    assert user.username == "findme"

def test_get_user_by_username_not_found(db):
    user = crud.get_user_by_username(db, "doesnotexist")
    assert user is None

def test_create_note(db):
    user = crud.create_user(db, schemas.UserCreate(
        username="noteowner",
        password="securepass123"
    ))
    note = crud.create_note(db, schemas.NoteCreate(
        title="My Note",
        content="Some content"
    ), user.id)
    assert note.content == "Some content"
    assert note.title == "My Note"
    assert note.owner_id == user.id
    assert note.id is not None

def test_get_notes_empty(db):
    user = crud.create_user(db, schemas.UserCreate(
        username="emptyuser",
        password="securepass123"
    ))
    result = crud.get_notes(db, user.id)
    assert result["total"] == 0
    assert result["notes"] == []

def test_get_notes_search(db):
    user = crud.create_user(db, schemas.UserCreate(
        username="searchuser",
        password="securepass123"
    ))
    crud.create_note(db, schemas.NoteCreate(content="Buy milk"), user.id)
    crud.create_note(db, schemas.NoteCreate(content="Call doctor"), user.id)
    result = crud.get_notes(db, user.id, search="milk")
    assert result["total"] == 1
    assert result["notes"][0].content == "Buy milk"

def test_delete_note(db):
    user = crud.create_user(db, schemas.UserCreate(
        username="deleteuser",
        password="securepass123"
    ))
    note = crud.create_note(db, schemas.NoteCreate(
        content="Delete me"
    ), user.id)
    deleted = crud.delete_note(db, note.id, user.id)
    assert deleted is not None
    assert crud.get_note(db, note.id, user.id) is None

def test_update_note(db):
    user = crud.create_user(db, schemas.UserCreate(
        username="updateuser",
        password="securepass123"
    ))
    note = crud.create_note(db, schemas.NoteCreate(
        content="Original"
    ), user.id)
    updated = crud.update_note(db, note.id, schemas.NoteUpdate(
        content="Updated"
    ), user.id)
    assert updated.content == "Updated"