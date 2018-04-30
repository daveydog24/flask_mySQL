# importing everything to complete the assingment
from flask import Flask, render_template, request, redirect, flash, session
import re
import md5
from datetime import datetime
from mysqlconnection import MySQLConnector

# creating the app, secretkey, email_regex format, and connecting mysql to my program and servver
app = Flask(__name__)
app.secret_key = 'WallAssignment'
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnector(app,'wall')

# basic home route that displays the intital html page
@app.route('/')
def index():
    return render_template("index.html")

# login route to process data and see if the user is in the database and the email and password match up
# will redirect to the wall if successfull and back to the index/homepage if not
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
        return redirect('/wall')

    flash(' Invalid email/password')
    return redirect('/')

# this route processes all the registration info 
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
    # stores a flash method if the email is invalid
    else:
        flash('invalid email address, try again')
    
    # conditional to check the first name is valid and fits the format we ask for then stores the name in session
    if len(first_name) > 1 and first_name.isalpha():
        session['first_name'] = first_name
        session['count_test'] += 1
    # if conditional fails it stores a flash method with invalid format
    else:
        flash('invalid first name input, try again')

    # conditional to check the last name is valid and fits the format we ask for then stores the name in session
    if len(last_name) > 1 and last_name.isalpha():
        session['last_name'] = last_name
        session['count_test'] += 1
    # if conditional fails it stores a flash message with invalid format
    else:
        flash('invalid last name input, try again')

    # checks to see if the password is in a proper format and then an inner conditional to check the passwords match
    if len(password) >= 8: 
        if len(confirm_password) >= 8: 
            if confirm_password == password:
                session['password'] = md5.new(password).hexdigest()
                session['confirm_password'] = md5.new(confirm_password).hexdigest()
                session['count_test'] += 1
            # if neseted conditional fails it stores a flash message with an unmatched password
            else:
                flash('password does not match, try again')  
    # if conditional fails it stores a flash method with the password failing the format provided
    else:
        flash('invalid password format, try again')

    # checks the stored varibale from earlier and if all conditionals were met then we move forward with storing the data
    if int(session['count_test']) == 4:
        query = "SELECT * FROM users WHERE email=:email"
        data = {'email': request.form['email']}
        result = mysql.query_db(query, data)

        # conidtional will check if the valid information already is stored in the database and if it is will redirect back to the index/homepage
        if len(result) != 0:
            flash("Email already exists in database")
            return redirect('/')

        # We'll then create a dictionary of data from the POST data received if its not in the system
        flash("Thanks for submitting your information.")
        session.pop('count_test')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        data = {
                'first_name': session['first_name'], 
                'last_name': session['last_name'], 
                'email': session['email'], 
                'password': md5.new(session['password']).hexdigest()
            }
        mysql.query_db(query, data)

        # now we will select all the information we will need to move the user logged in forward and direct to the wall
        query = "SELECT id, first_name FROM users WHERE first_name=:first_name AND last_name=:last_name AND email=:email"
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        user = mysql.query_db(query, data)
        session.clear()
        session['id'] = user[0]['id']
        return redirect('/wall')
    else:
        return redirect('/')

# app that displays all the content from all users as well as storing information of the current logged in user
@app.route('/wall')
def wall():
    # will kick the user back if somehow they got to this page and no one is logged in saved in session
    if 'id' not in session:
        return redirect('/')

    # retrieving the information from the database of the current user and storing his full name 
    query = "SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users WHERE users.id = {}".format(session['id'])
    name = mysql.query_db(query)
    name = name[0]['full_name']

    # retrieving all the the messages we have stored in the database 
    query = "SELECT messages.id, messages.user_id, CONCAT(users.first_name, ' ', users.last_name) as posted_by, DATE_FORMAT(messages.created_at, '%M %D, %Y') as posted_on, messages.message as content FROM messages JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"
    messages = mysql.query_db(query)

    # retrieving all the comments we have stored in the database
    query = "SELECT comments.id, comments.user_id, comments.message_id, CONCAT(users.first_name, ' ', users.last_name) as posted_by, DATE_FORMAT(messages.created_at, '%M %D, %Y') as posted_on, comments.comment as content FROM comments JOIN messages ON comments.message_id = messages.id JOIN users ON messages.user_id = users.id"
    comments = mysql.query_db(query)

    return render_template("success.html", name=name, messages=messages, comments=comments)

# this route is designed to add the messages to the database
@app.route('/newMessages', methods=['POST'])
def newMessages():
    user_id = session['id']
    message = request.form['message']
    query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
    data = {
        'user_id': user_id,
        'message': message
    }
    # inserts the new message and links it to the current user that posted it in the database
    mysql.query_db(query, data)

    return redirect('/wall')

# this route is designed to add comments on messages
@app.route('/newComments/<message_id>', methods=['POST'])
def newComment(message_id):
    user_id = session['id']
    comment = request.form['comment']
    query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES (:message_id, :user_id, :comment, NOW(), NOW())"
    data = {
        'message_id': message_id,
        'user_id': user_id,
        'comment': comment
	}
    # query runs to store a comment linked directly to a specific message from the specific user
    mysql.query_db(query, data)

    return redirect('/wall')

# this route will delete messages
@app.route('/deleteMessage/<message_id>')
def deleteMessage(message_id):
    data = {
        'id': int(message_id)
    }
    # deletes the messages from the current id passed through
    query = "DELETE FROM messages WHERE messages.id=:id"
    mysql.query_db(query, data)

    # selects to see if there are comments attached to the current message select
    query = "SELECT * FROM comments WHERE comments.message_id=:id"
    # if so then it will go and delete the comments as well
    if len(mysql.query_db(query,data)) != 0:
        query = "DELETE FROM comments WHERE comments.message_id=:id"
        mysql.query_db(query, data)
    else:
        return redirect('/wall')

# route is designed to delete the a comment when the delete comment button is selected
@app.route('/deleteComment/<comment_id>')
def deleteComment(comment_id):
    # queries the data and deletes the current comment selected
    query = "DELETE FROM comments WHERE comments.id=:id"
    data = {
        'id': int(comment_id)
    }
    mysql.query_db(query, data)

    return redirect('/wall')

# this will clear all messages and things stored in session to start fresh when the user logs out
@app.route('/clear', methods=['POST'])
def clear():
    session.clear()
    return redirect('/')

app.run(debug=True)