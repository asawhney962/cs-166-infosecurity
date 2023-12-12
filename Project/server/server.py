# export FLASK_APP=server.py
# flask run --host=0.0.0.0
import hashlib
from flask import Flask, session, render_template, redirect, url_for, request
from flask_cors import CORS, cross_origin
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = 'SecretKey!23$'

CORS(app)
sess = Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config.from_object(__name__)

sess.init_app(app)
db.init_app(app)

# Track logged in user uids.
logged_in_uids = []

class User(db.Model):
    __tablename__ = 'users'
    UID = db.Column(db.Integer, primary_key=True)
    USER = db.Column(db.String)
    PASS = db.Column(db.String)

def HashPass(password=''):
    return str(hashlib.sha512(str(password).encode('utf-8')).hexdigest())

def IsLoggedIn(username):
    users = db.session.execute(db.select([User]))
    for user in users:
        if user.USER == username and user.UID in logged_in_uids:
            return True
    return False

def PerformLogin(username, password):
    global login_sessions
    passhash = HashPass(password)
    
    users = db.session.execute(db.select([User]))
    for user in users:
        # Add uid to logged in uid list.
        if user.USER == username and user.PASS == passhash:
            if user.UID not in logged_in_uids:
                logged_in_uids.append(user.UID)
            print('Logged in user ' + str(user.USER))
            return True
                
    # Invalid credentials.
    return False

def PerformLogout(username):
    global login_sessions
    
    users = db.session.execute(db.select([User]))
    for user in users:
        if user.USER == username and user.UID in logged_in_uids:
            logged_in_uids.remove(user.UID)
            print('Logged out user ' + str(user.USER))
    
    return

# Discourage caching for easier testing.
@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    return response

# Test page to print database entries.
@app.route('/users')
def users():
    try:
        users = db.session.execute(db.select([User]).order_by(User.UID))
        users_text = '<ul>'
        for user in users:
            users_text += '<li>' + str(user.UID) + ', ' + str(user.USER) + ', ' + str(user.PASS) + '</li>'
        users_text += '</ul>'
        return users_text
    except Exception as e:
        return '<p>Error:<br>' + str(e) + '</p>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in, redirect to home page.
    if 'username' in session and IsLoggedIn(session['username']):
        return redirect(url_for('home'))
    
    # Show login form.
    if request.method == 'GET':
        return render_template('login.html', status=request.args.get('status'))
    # Attempt login.
    elif request.method == 'POST':
        # Get credentials from login form.
        username = request.form['username']
        password = request.form['password']
        
        # Verify that inputs are not empty.
        if not username:
            return redirect(url_for('login', status='Username cannot be empty.'))
        
        if not password:
            return redirect(url_for('login', status='Password cannot be empty.'))
        
        # Attempt login.
        if not PerformLogin(username, password):
            return redirect(url_for('login', status='Invalid credentials.'))
        
        # Logged in, set session data and redirect to home page.
        session['username'] = username
        return redirect(url_for('home'))
    
    # Redirect back to home page for all other methods.
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    # Clear session if user is logged in.
    if 'username' in session and IsLoggedIn(session['username']):
        PerformLogout(session['username'])
        session.clear()
    
    # Redirect to home page.
    return redirect(url_for('home'))

@app.route('/')
@app.route('/home')
def home():
    username = None
    
    # Check if user has an active session.
    if 'username' in session and IsLoggedIn(session['username']):
        username = session['username']
    
    return render_template('home.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
