from pydantic import BaseModel,validator
import re

class UserIn(BaseModel):
    username: str
    email: str
    password: str
    place:str

    @validator ("password")
    def validate_password(cls, value):
        if not re.search(r'[a-z]', value):
            raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
        if not re.search(r'[A-Z]', value):
            raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
        if not re.search(r'\d', value):
            raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
        if not re.search(r'[^\w\s]', value):
            raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
        return value
    @validator ('email')
    def validate_email(cls,value):
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',value):
            raise ValueError('Not a Valid Email')
        return value

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    place:str

    class Config:
        orm_mode = True



# class reviews(BaseModel):
#     product_name : str
#     brand_name :str 
#     price : str
#     rating :int 
#     review :str
#     review_votes :int

# class Updata_User(BaseModel):
#     new_password: str
#     @validator ("password")
#     def validate_password(cls, value):
#         if not re.search(r'[a-z]', value):
#             raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
#         if not re.search(r'[A-Z]', value):
#             raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
#         if not re.search(r'\d', value):
#             raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
#         if not re.search(r'[^\w\s]', value):
#             raise ValueError('password must contain at least one lowercase letter,uppercase letter,digit,special character')
#         return value

