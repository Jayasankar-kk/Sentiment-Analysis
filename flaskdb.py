
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
basedir =os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data01.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db1=SQLAlchemy(app)
db1.init_app(app)
