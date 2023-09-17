from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit
import hashlib
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CHANGE_THIS'

# Configure MySQL connection
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'flaschat'
app.config['MYSQL_PASSWORD'] = 'h8r9BKbFNvEgYxS'
app.config['MYSQL_DB'] = 'message_db'

MAX_MSG_LEN = 500
MAX_USERNAME_LEN = 13

mysql = MySQL(app)

socketio = SocketIO(app)


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM messages ORDER BY id DESC LIMIT 30')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages[::-1], username=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, hashed_password))
            user = cur.fetchone()
            cur.close()
        except Exception:
            print("Error logging in")
            flash("Could not login!")

        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Validate input data
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address')
        elif not re.match(r'^\w+$', username):
            flash('Username must contain only letters, numbers, or underscores')
        elif not username or not password or not email:
            flash('Please fill out the form')
        else:
            # Insert new user into database
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)',
                        (username, hashed_password, email))
            mysql.connection.commit()
            cur.close()
            return redirect("/login")

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@socketio.on('send_message')
def handle_send_message(data):
    username = data['username']
    content = data['content']
    if 'username' not in session:
        return
    if content == "": return
    if len(content) > MAX_MSG_LEN:
        emit('send_error', {'error': f"Length over {MAX_MSG_LEN} characters", 'content': content}, broadcast=True,
             json=True)
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (username, content) VALUES (%s, %s)', (username, content))
    mysql.connection.commit()
    cur.close()
    emit('receive_message', {'username': username, 'content': content}, broadcast=True, json=True)


if __name__ == '__main__':
    socketio.run(app, debug=False, host="0.0.0.0", port=5000)
