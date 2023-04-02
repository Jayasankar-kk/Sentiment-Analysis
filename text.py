from fastapi import Depends, FastAPI,HTTPException,status,UploadFile, File, BackgroundTasks
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
from fastapi import APIRouter
import numpy as np
from transformers import pipeline

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from users1 import logging, logger
import json
import csv






def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()

import pandas as pd
import numpy as np
from transformers import pipeline

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/get/token/")

#Function to do sentiment Analysis
def sent_analysis(db_id,db: Session= Depends(get_db) ):
  #reading a sqltable and converting into pandas dataframe
  status_row = db.query(models.Statustable).filter(models.Statustable.id == db_id).first()
  # Extract the json_data from the status row
  json_data = status_row.file
  # Convert JSON data to DataFrame
  df = pd.read_json(json_data)
  #converting the review column of the dataframe into a list and setting max_lenght
  reviews = list(df['Reviews'])
  max_length = 512
  try:
    #Using list comprehension to set maxlength for each rows of column Reviews and storing them as a list
    reviews = [r[:max_length] for r in df['Reviews']] 
    #defining the classifier using pipeline and default model distilbert-base-uncased
    classifier = pipeline('sentiment-analysis',model='distilbert-base-uncased')
    #Doing the analyssis by passing the reviews into the classifier
    sent_analysis = classifier(reviews)
    #Getting the values under the key labels
    labels = [dic['label'] for dic in sent_analysis]
    #passing the labels as a column to the df
    df['Sentiment Analysis'] = labels
    #selecting the required columns from df
    select_columns = df[['Product Name','Reviews','Sentiment Analysis']]
    #converting the df into a json string and storing in db
    json_str = select_columns.to_json()
    db.query(models.Statustable).filter(models.Statustable.id == db_id).update({'data':json_str,'status': 1})
    db.commit()
    db.close()
    logger.info("Sentimental Analysis Done")
  except Exception as e:
    logger.debug ('Processing failed:%s', e)
    db.query(models.Statustable).filter(models.Statustable.id == db_id).update({'status': 2})
    db.commit()
    db.close()
  

router = APIRouter()
#endpoint to upload file and do the analysis as background task
@router.post("/file_upload")
async def image_detection(image: UploadFile, background_tasks: BackgroundTasks,tocken: str= Depends(oauth2_scheme),db: Session = Depends(get_db)):
    # Save the uploaded image to a local file
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    
    user_name = crud.validate_tocken(db,tocken)
    logger.debug('file_name: %s', user_name)
    if user_name == "Could not validate credentials":
       logger.debug("Invalid tocken")
       raise credentials_exception
    else:
        logger.debug("username for statustable: %s",user_name)
        csv_data = await image.read()

        # Convert CSV data to a list of dictionaries
        csv_dict = csv.DictReader(csv_data.decode().splitlines())

        # Convert the list of dictionaries to JSON format
        json_data = json.dumps(list(csv_dict))
        print("##############",user_name)
        crud.status_table(db,user_name,json_data)

        # Schedule the background task to perform image detection
        db_id = crud.return_db_id(db)
        logger.debug("db_id: %s",db_id)
        background_tasks.add_task(sent_analysis, db_id, db)
        logger.info("Background task added")
        return JSONResponse(content={"db_id": db_id})






#endpointt to know the status of background task 
@router.get ("/status")
async def sent_analysis_status(db_id: int,Authorization: str= Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    validation = crud.validate_tocken(db,Authorization)
    if validation == "Could not validate credentials":
       raise credentials_exception
    else:
        status1 = db.query(models.Statustable.status).filter(models.Statustable.id == db_id).scalar()
        if status1 == 0:
            return {"status": "progressing"}
        elif status1 == 1:
            return {"status": "success"}
        elif status1 == 2:
            return {"status": "failed"}
  
