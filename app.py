from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'supersecretkey'

DB_PATH = 'users.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            name TEXT,
            birthday TEXT,  -- store as string YYYY-MM-DD
            address TEXT,
            image TEXT
         );
         ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect(url_for('profile'))
        else:
            return "Login failed!"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']
        image = None

        if 'image' in request.files:
            img = request.files['image']
            if img.filename != '':
                image_path = os.path.join('static/uploads', img.filename)
                img.save(image_path)
                image = img.filename

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (username, password, name, birthday, address, image)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password, name, birthday, address, image))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, birthday, address, image FROM users WHERE username = ?', (username,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        name, birthday_str, address, image = user_data

        # Compute age
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

        return render_template('profile.html', name=name, age=age, address=address, image=image)
    else:
        return "User data not found", 404


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
