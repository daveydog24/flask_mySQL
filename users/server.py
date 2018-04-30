from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app,'friendsdb')

@app.route('/')
def index():                         
    return render_template('index.html') 

@app.route('/results', methods=['POST'])
def create():
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO friends (first_name, last_name, email, created_at, updated_at) VALUES (:first_name, :last_name, :email, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'first_name': request.form['first_name'],
             'last_name':  request.form['last_name'],
             'email': request.form['email']
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    return redirect('/users')

@app.route('/users')
def users():
    query = "SELECT friends.id, friends.email, friends.first_name, friends.last_name, DATE_FORMAT(friends.created_at, '%M %D, %Y') AS created_at FROM friends"
    users = mysql.query_db(query)
    return render_template('users.html', users= users)

@app.route('/user/new')
def new_user():
    return render_template('new_user.html')

@app.route('/user/<user_id>')
def show(user_id):
    # Write query to select specific user by id. At every point where
    # we want to insert data, we write ":" and variable name.
    query = "SELECT friends.id, friends.email, friends.first_name, friends.last_name, DATE_FORMAT(friends.created_at, '%M %D, %Y') AS created_at FROM friends WHERE id = :specific_id"
    # Then define a dictionary with key that matches :variable_name in query.
    data = {'specific_id': user_id}
    # Run query with inserted data.
    users = mysql.query_db(query, data)
    # Friends should be a list with a single object,
    # so we pass the value at [0] to our template under alias one_friend.
    return render_template('user.html', users=users)

@app.route('/user/<user_id>/edit')
def edit(user_id):
    query = "SELECT friends.id, friends.email, friends.first_name, friends.last_name, DATE_FORMAT(friends.created_at, '%M %D, %Y') AS created_at FROM friends WHERE id = :specific_id"
    data = {'specific_id': user_id}
    users = mysql.query_db(query, data)

    return render_template('update_user.html', users=users, user_id=user_id)

@app.route('/update_user/<user_id>', methods=['POST'])
def update(user_id):
    query = "UPDATE friends SET first_name = :first_name, last_name = :last_name, email = :email WHERE id = :id"
    data = {
             'first_name': request.form['first_name'],
             'last_name':  request.form['last_name'],
             'email': request.form['email'],
             'id': user_id
           }
    mysql.query_db(query, data)
    return redirect('/users')

@app.route('/remove_user/<user_id>')
def delete(user_id):
    query = "DELETE FROM friends WHERE id = :id"
    data = {'id': user_id}
    mysql.query_db(query, data)
    return redirect('/users')

app.run(debug=True)