from crud import *
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app
import pytest
from database import SessionLocal
from models import User

@pytest.fixture
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()


#To test if a user exist inn db
#Case 1: giving an existing username
def test_get_user_by_username_already_exists(get_db):
    user = get_user_by_username(get_db, username='Sanju')
    assert isinstance(user, User)
    assert user.username == 'Sanju'

#Case 2: giving a non existant username
def test_create_user_username_not_already_exists(get_db):
    user = get_user_by_username(get_db, username='Rajesh')
    assert user == None

# to test validate_tocken function

#Case1: testing with a valid tocken using the name of user in db
def test_validate_token(get_db):
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    valid_token = create_access_token(data={"sub":'Sanju'}, expires_delta=access_token_expires)
    assert validate_tocken(get_db,valid_token) == "validated"

#Case2: testing with an invalid tocken generated from a name which is not that of a user
def test_validate_invalidtoken(get_db):
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    valid_token = create_access_token(data={"sub":'Rajesh'}, expires_delta=access_token_expires)
    assert validate_tocken(get_db,valid_token) == "Could not validate credentials"



