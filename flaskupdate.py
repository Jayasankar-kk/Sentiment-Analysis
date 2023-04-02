import requests
from sqlalchemy.orm import Session
from flask import Flask,request,render_template,flash,redirect,session,get_flashed_messages
from flask import url_for
from database import SessionLocal, engine
import crud, models, schemas
from flaskform import *
#from flask_login import login_user,login_required, logout_user, current_user
import os
from flask import jsonify
from werkzeug.utils import secure_filename
import io
from sqlalchemy import Table,MetaData
import sqlalchemy as db
import pandas as pd
from io import StringIO
from flask import make_response
import json
from users1 import logging, logger
import tempfile

app = Flask(__name__)
app.secret_key = 'mysecretkey'

#Creating an instance of SessionLocal
session1 = SessionLocal()



def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()


app.config['SECRET_KEY'] = 'mysecretkey'


##Function to Signup
@app.route('/signup',methods = ["GET","POST"])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        email = form.email.data
        place = form.place.data
        url = 'http://localhost:8000/create/user/'
        data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'place': place
                }
        response = requests.post(url,json=data)
        logger.debug("Flask Signup response: %s",response.status_code)
        if response.status_code == 200:
            flash('Signup was successful')
            return render_template('index.html')
        else:
            if response.status_code == 422:
                try:
                    flash(response.json()["detail"][0]['msg'])
                except:
                    flash(response.json()['detail'])

    return render_template('signup.html',form = form)

#Function to signin
@app.route('/signin',methods = ["GET","POST"])
def signin():
    form = SigninForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        url = 'http://localhost:8000/get/token/'
        data1 = {
                    'username': username,
                    'password': password,
                }
        response = requests.post(url,data=data1)
        logger.debug("Flask Signin response: %s",response.status_code)
        if response.status_code == 200:
            tocken = response.json()['access_token']
            session['tocken'] = tocken 
            return render_template('profile.html', username=username, tocken=tocken)
        else:
            flash('Invalid username or password')
    return render_template('signin.html', form =form)
#function to display profile page
@app.route('/profile',methods = ["GET"])
def profile():
    return render_template('profile.html')

#function to delete profile 
@app.route('/profile/del', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        username = request.form['username']
        url = "http://localhost:8000/deleteuser"
        response = requests.delete(url,params={'username': username})
        logger.debug("Flask delete profile response: %s",response.status_code)
        if response.status_code == 200:
            flash(f'Profile of {username} has been deleted')
            return render_template('index.html')
        else:
            return render_template('delete.html')
    

#function to change password
@app.route('/profile/password_change', methods=['GET', 'POST'])
def password_change():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        newpassword = request.form['newpassword']
        url = "http://localhost:8000/passwordchange/"
        response = requests.post(url, params={'username': username, 'password': password, 'newpassword': newpassword})
        logger.debug("Flask password change response: %s",response.status_code)
        if response.status_code == 200:
            flash('Password changed successfully!', 'success')
        else:
            flash('Password change failed!', 'error')
        
        return redirect(url_for('password_change'))
    
    return render_template('password.html')


#function to upload file
@app.route('/file_upload', methods=['POST'])
def upload_csv():
    try:
        if request.method == 'POST':
            tocken = request.form['tocken']
            file = request.files['file']
            filename = file.filename
            # Save the uploaded file to a local directory
            tmpdir = tempfile.TemporaryDirectory()
            file_path = os.path.join(tmpdir.name, filename)
            file.save(file_path)
            headers = {'Authorization': 'Bearer ' + tocken}
            # Upload the file to the FastAPI endpoint
            with open(file_path, 'rb') as f:
                file_contents = f.read()
                files = {'image': (filename, file_contents)}
                url = 'http://localhost:8000/file_upload'
                response = requests.post(url, headers= headers, files=files)
                response_data = json.loads(response.content.decode())
                session['db_id'] = int(response_data['db_id'])
            return render_template('dbid.html',id = response.content)
    except:
        return "Session timed out. Please login!!"

# to get the status of background task and display the table 
@app.route('/output')
def analysis():
    db_id = session['db_id']
    tocken = session['tocken']
    record = session1.query(models.Statustable).filter(models.Statustable.id == db_id).first()
    url = "http://localhost:8000/status"
    headers = {'Authorization': f'Bearer {tocken}'}
    response = requests.get(url,headers=headers,params={'db_id': db_id})
    print(response.json)
    status = response.json()['status']
    logger.debug("Flask status: %s",status)
    if record and status == 'success':
        data = pd.read_json(record.data)
        data_dict = data.to_dict('records')
        return render_template('newoutput.html', data=data_dict)
    elif status == 'progressing':
        # if the record does not exist, return an error message
        return '<h1>Sentiment Analysis is Progressing...</h1>'
    elif status == 'failed':
        return '<h1> Sentiment Analysis has failed!!!</h1>'


# to download the analysis in csv format
@app.route('/download')
def download():
    db_id = session['db_id']
    record = session1.query(models.Statustable).filter(models.Statustable.id == db_id).first()
    df = pd.read_json(record.data)
    csv_string = df.to_csv(index=False)
    csv_file = StringIO(csv_string)
    response = make_response(csv_file.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=analysis_table.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


#end point to the index 
@app.route('/')
def index():
   return render_template('index.html')


#to display all users
# @app.route('/users')
# def users():
#     users = session1.query(models.User).all()
#     return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)