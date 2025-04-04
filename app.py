from flask import Flask, flash, session
from routes import register_routes
import sqlite3
from routes import UserSession

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random string in production

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
                security_q3 TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                model TEXT NOT NULL,
                make TEXT NOT NULL,
                year INTEGER NOT NULL,
                mileage INTEGER NOT NULL,
                color TEXT,
                price REAL NOT NULL,
                location TEXT NOT NULL,
                precise_location TEXT,
                is_available BOOLEAN DEFAULT 1,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                renter_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                total_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE,
                FOREIGN KEY(renter_id) REFERENCES users(id) ON DELETE CASCADE
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                payer_id INTEGER NOT NULL,
                payee_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_confirmed BOOLEAN DEFAULT 1,
                FOREIGN KEY(booking_id) REFERENCES bookings(id),
                FOREIGN KEY(payer_id) REFERENCES users(id),
                FOREIGN KEY(payee_id) REFERENCES users(id)
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                reviewer_id INTEGER NOT NULL,
                reviewee_id INTEGER NOT NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(booking_id) REFERENCES bookings(id),
                FOREIGN KEY(reviewer_id) REFERENCES users(id),
                FOREIGN KEY(reviewee_id) REFERENCES users(id)
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_recovery_chain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                step_order INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        ''')
        conn.commit()

# Global context processor to make UserSession information available in templates
@app.context_processor
def inject_user_session():
    return dict(is_authenticated=UserSession.get_instance().is_authenticated())
register_routes(app)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
