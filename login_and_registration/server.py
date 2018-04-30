from flask import Flask, render_template, request, redirect, flash, session
import re
import md5
from datetime import datetime
from mysqlconnection import MySQLConnector

app = Flask(__name__)
app.secret_key = 'RegistrationAssignment'
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnector(app,'mydb')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE email=:email AND password=:password"
    data = {
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest()
        }
    results = mysql.query_db(query, data)

    if len(results) != 0:
        result = results[0]
        session['id']=result['id']
        flash("Welcome Back!")
        return redirect('/results')

    flash(' Invalid email/password')
    return redirect('/')

@app.route('/results')
def results():
    if 'id' not in session:
        email = session['email']
        first_name = session['first_name']
        last_name = session['last_name']
        password = md5.new(session['password']).hexdigest()
        return render_template("success.html", email=email, first_name=first_name, last_name=last_name, password=password)
    else:
        query = "SELECT * FROM users WHERE id= {}".format(session['id'])
        user = mysql.query_db(query)
        user = user[0]
        email = user['email']
        first_name = user['first_name']
        last_name = user['last_name']
        password = md5.new(user['password']).hexdigest()
        return render_template("success.html", email=email, first_name=first_name, last_name=last_name, password=password)

@app.route('/registration', methods=['POST'])
def result():
    session.clear()
    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = md5.new(request.form['password']).hexdigest()
    confirm_password = md5.new(request.form['confirm_password']).hexdigest()

    # overall test that will make sure all information is valid when registered
    if 'count_test' not in session:
        session['count_test'] = 0

    # conditional to check if the email entered is valid and stores a session variable if it does
    if email_regex.match(email):
        session['email'] = email
        session['count_test'] += 1
    else:
        flash('invalid email address, try again')
        # stores a flash method if the email is invalid
    
    # conditional to check the first name is valid and fits the format we ask for then stores the name in session
    if len(first_name) > 1 and first_name.isalpha():
        session['first_name'] = first_name
        session['count_test'] += 1
    else:
        flash('invalid first name input, try again')
        # if conditional fails it stores a flash method with invalid format

    # conditional to check the last name is valid and fits the format we ask for then stores the name in session
    if len(last_name) > 1 and last_name.isalpha():
        session['last_name'] = last_name
        session['count_test'] += 1
    else:
        flash('invalid last name input, try again')
        # if conditional fails it stores a flash message with invalid format

    # checks to see if the password is in a proper format and then an inner conditional to check the passwords match
    if len(password) >= 8: 
        if len(confirm_password) >= 8: 
            if confirm_password == password:
                session['password'] = password
                session['confirm_password'] = confirm_password
                session['count_test'] += 1
            else:
                flash('password does not match, try again')  
                # if conditional fails it stores a flash message with an unmatched password
    else:
        flash('invalid password format, try again')
        # if conditional fails it stores a flash method with the password failing the format provided

    # checks the stored varibale from earlier and if all conditionals were met then we move forward with storing the data
    if int(session['count_test']) == 4:
        query = "SELECT * FROM users WHERE email=:email"
        data = {'email': request.form['email']}
        result = mysql.query_db(query, data)
        if len(result) != 0:
            flash("Email already exists in database")
            return redirect('/')

        flash("Thanks for submitting your information.")
        session.pop('count_test')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        # # We'll then create a dictionary of data from the POST data received.
        data = {
                'first_name': session['first_name'], 
                'last_name': session['last_name'], 
                'email': session['email'], 
                'password': session['password']
            }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)
        return redirect('/results')

    # atleast one form was not valid/password didnt match so they are returned to the registration page and flashed what failed
    else:
        return redirect('/')

# clears the user logged in stored in session if the click the logout button
@app.route('/clear', methods=['POST'])
def clear():
    session.clear()
    return redirect('/')

app.run(debug=True)