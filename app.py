from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database Initialization
DATABASE = "database.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                security_q1 TEXT NOT NULL,
                security_q2 TEXT NOT NULL,
                security_q3 TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                mileage INTEGER NOT NULL,
                availability TEXT NOT NULL,
                price REAL NOT NULL,
                location TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

# Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        security_q1 = request.form['security_q1']
        security_q2 = request.form['security_q2']
        security_q3 = request.form['security_q3']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password, security_q1, security_q2, security_q3) VALUES (?, ?, ?, ?, ?)",
                           (email, password, security_q1, security_q2, security_q3))
            conn.commit()
        return redirect(url_for('home'))
    return render_template("register.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
