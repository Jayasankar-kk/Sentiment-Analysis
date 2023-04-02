from fastapi import APIRouter
from fastapi import Depends, FastAPI,HTTPException,status,UploadFile, BackgroundTasks
from typing import List
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi.responses import JSONResponse
import pandas as pd
import database
import csv
models.Base.metadata.create_all(bind=engine)
import logging
from fastapi import Form

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler('myapp.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)



def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()



router = APIRouter()
#end point to create user
@router.post("/create/user/", response_model=schemas.User)
def create_user(user: schemas.UserIn, db: Session =Depends(get_db)):
  db_user = crud.get_user_by_username(db, username=user.username)
  if db_user:
    logger.warning("Username exists")
    raise HTTPException(status_code=422, detail="username already exists")
  if not schemas.UserIn.validate_password(user.password):
    logger.warning("password error")
    raise HTTPException(status_code=422,
                         detail=error_detail)
  if not schemas.UserIn.validate_email(user.email):
    logger.warning("email error")
    raise HTTPException(status_code=422,detail=error_detail)
  return crud.create_user(db=db, user=user)

#endpoint to get users
@router.get("/get/users/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
  users = crud.get_users(db)
  logger.debug("Users",users)
  return users


#to get tocken
@router.post("/get/token/")
async def login_for_access_token(db: Session = Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",
                        headers={"WWW-Authenticate": "Bearer"},)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = crud.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    logger.debug("Access token: %s", access_token)
    return {"access_token": access_token, "token_type": "bearer"}

#endpoint for password change
@router.post("/passwordchange/")
async def password_change(username: str,password:str,newpassword:str, db: Session = Depends(get_db)):
  user = crud.authenticate_user(db,username,password)
  logger.debug("user for password change: %s", user)
  if not user:
    raise HTTPException(status_code=401, detail="Invalid User")
  else:
    schemas.UserIn.validate_password(newpassword)
    crud.change_password(db,username,newpassword)
    return JSONResponse(content={"message": "Password updated"})


#endpoint for deleting the user 
@router.delete("/deleteuser/")
async def delete_user(username: str,db: Session = Depends(get_db)):
  user = db.query(models.User).filter(models.User.username == username).first()
  if not user:
        raise HTTPException(status_code=404, detail="User not found")
  db.delete(user)
  db.commit()
  logging.info('User Deleted')
  return {"message": "User deleted successfully"}


