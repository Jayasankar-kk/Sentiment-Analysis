from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField

class SignupForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("passsword")
    email = StringField("Email")
    place = StringField("place")
    submit = SubmitField('signup')

class SigninForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField ("passsword")
    submit = SubmitField('signin')


class upload(FlaskForm):
    tocken = StringField("Tocken")
    submit = SubmitField('Submit')

class Status(FlaskForm):
    tocken = StringField("Tocken")
    db_id = IntegerField("DB_id")
