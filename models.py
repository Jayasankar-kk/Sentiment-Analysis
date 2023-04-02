

from sqlalchemy import Boolean, Column, Integer, String,Table,MetaData,JSON
from database import Base,engine
from sqlalchemy import Column, Integer, LargeBinary,Float
# Create SQLAlchemy models from the Base class
class User(Base):
    __tablename__ = "users"

    # Create model attributes/columns
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    place=Column(String)




class Statustable(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, index=True)
    file = Column(String)
    username = Column(String)
    data = Column(String)
    status = Column(Integer)







