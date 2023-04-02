
from fastapi import Depends, FastAPI,HTTPException,status,UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
import datetime
from datetime import timedelta
import csv
import pandas as pd
import database
import logging



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='myapp.log',
                    filemode='w')

# function to get all users
def get_users(db: Session):
   return db.query(models.User).all()

#function to get a user by name
def get_user_by_username(db: Session, username: str):
   user = db.query(models.User).filter(models.User.username == username).first()
   db.close()
   return user
#function to create a new user 
def create_user(db: Session, user: schemas.UserIn):
    pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")
    hashed_pwd = pwd_context.hash(user.password)
    db_user = models.User(username = user.username, email=user.email,password=hashed_pwd,place=user.place)
    db.add(db_user) # add that instance object to your database session
    db.commit() # commit the changes to the database (so that they are saved).
    db.refresh(db_user) # refresh your instance
    db.close()
    return db_user


# to verify if a received password matches the hash stored

def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

#to authenticate whther the username and password entered matches the one in db
def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


#to create acceess tocken 
def create_access_token(data: dict, expires_delta):
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#to validate_tocken and return if validated or not
def validate_tocken(db: Session,tocken):
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    try:
        payload = jwt.decode(tocken, SECRET_KEY, algorithms=ALGORITHM)
        name = payload.get("sub")
        username = get_user_by_username(db,name)
        if username is None:
            return "Could not validate credentials"
        else:
            return name
    except JWTError:
        return "Could not validate credentials"

# to return db_id
def return_db_id(db: Session):
     reviews = db.query(models.Statustable).order_by(models.Statustable.id.desc()).first()
     db.close()
     return reviews.id

#to change password
def change_password(db: Session,username, newpassword):
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pwd = pwd_context.hash(newpassword)
        db.query(models.User).filter(models.User.username == username).update({'password': hashed_pwd})
        db.commit()
        return 'success'
    except Exception as e:
        db.rollback()
        db.close()
        return {"error": str(e)}
    

#to insert values into status table
def status_table(db: Session,username:str,input:str):
    db_user = models.Statustable(file=input, username= username, data = 'null',status=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

#to fetch the status by inserting db_id
def get_status_by_id(db: Session, db_id: int):
    q1 = db.query(models.Statustable).filter(models.Statustable.id == db_id).first()
    db.close()
    return q1
#to update the status if successful
def update_status1(db: Session,db_id):
    db.query(models.Statustable).filter(models.Statustable.id == db_id).update({'status': 1})
    db.close()

#to update the status if failed
def update_status2(db: Session,db_id):
    db.query(models.Statustable).filter(models.Statustable.id == db_id).update({'status': 2})
    db.close()
