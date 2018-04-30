from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app,'mydb')
app.secret_key="emailassingment"

@app.route('/')
def index():
    return render_template('index.html') # pass data to our template

@app.route('/email', methods=['POST'])
def create():
    email = request.form['email']
    if email_regex.match(email): 
        query = "INSERT INTO email (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
        # We'll then create a dictionary of data from the POST data received.
        data = {
                'email': request.form['email']
            }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)
        flash('The email address you entered (' + email + ') is a VALID email address! Thank you!')
        return redirect('/success')
    else:
        flash('Email is not Valid!')
        return redirect('/')
    
#creates an app and function that selects all the information in the email database and renders the html
@app.route('/success')
def success():
    query = "SELECT DATE_FORMAT(created_at,' %m/%d/%Y %I:%m%p') AS DATE, email.email, email.id FROM email"               
    emails = mysql.query_db(query)
    return render_template('success.html', emails=emails)

@app.route('/delete/<user_id>')
def delete(user_id):
    query = "DELETE FROM email WHERE id=:specific_id;"
    data = {
        "specific_id":user_id,
    }          
    user = mysql.query_db(query, data)
    return redirect('/success')

app.run(debug=True)
