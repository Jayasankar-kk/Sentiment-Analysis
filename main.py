
from fastapi import FastAPI
from users1 import router as users_router
from text import router as text_router 
import logging


app = FastAPI()

app.include_router(users_router)
app.include_router(text_router)








      
   
