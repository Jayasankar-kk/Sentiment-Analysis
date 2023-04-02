from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create a database URL for SQLAlchemy
DATABASE_URL = "postgresql://uighj88f1fg7s0utkkxm:1f03EXBw5eVBz67Gl6SOp6DNNay26T@bkyi3blsdgi3ig1pmuuv-postgresql.services.clever-cloud.com:5432/bkyi3blsdgi3ig1pmuuv"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

# Create a Base class
Base = declarative_base()



  
