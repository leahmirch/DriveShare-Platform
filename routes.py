from flask import render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Singleton Pattern for Session
class UserSession:
    _instance = None

    def __init__(self):
        if UserSession._instance is not None:
            raise Exception("Singleton already exists!")
        self.user_id = None
        self.email = None
        self.role = None
        UserSession._instance = self

    @staticmethod
    def get_instance():
        if UserSession._instance is None:
            UserSession()
        return UserSession._instance

    def login(self, user_id, email, role):
        self.user_id = user_id
        self.email = email
        self.role = role

    def logout(self):
        self.user_id = None
        self.email = None
        self.role = None

    def is_authenticated(self):
        return self.user_id is not None





def register_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/booking/<int:car_id>", methods=["GET", "POST"])
    def booking(car_id):
        if request.method == "POST":
            return redirect(url_for("booking_confirmation"))
        return render_template("booking.html", car_id=car_id)

    @app.route("/booking_confirmation")
    def booking_confirmation():
        return render_template("booking_confirmation.html")

    @app.route("/car/<int:car_id>")
    def car_detail(car_id):
        return render_template("car_detail.html", car_id=car_id)

    @app.route("/dashboard")
    def dashboard():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to access the dashboard.")
            return redirect(url_for("login"))
        return render_template("dashboard.html")
    
    @app.route("/edit_car/<int:car_id>", methods=["GET", "POST"])
    def edit_car(car_id):
        if request.method == "POST":
            return redirect(url_for("manage_cars"))
        return render_template("edit_car.html", car_id=car_id)
    
    @app.route("/forgot_password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form["email"]
            new_password = request.form["new_password"]  # Assume the form includes a new_password field

            # Retrieve security question answers from the form
            answer1 = request.form.get("security_q1", "")
            answer2 = request.form.get("security_q2", "")
            answer3 = request.form.get("security_q3", "")

            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    # Fetch stored security questions for the user
                    cursor.execute("SELECT security_q1, security_q2, security_q3 FROM users WHERE email = ?", (email,))
                    user = cursor.fetchone()

                    if user and user == (answer1, answer2, answer3):
                        # If security answers match, update the password
                        hashed_password = generate_password_hash(new_password)
                        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
                        conn.commit()

                        flash("Password reset successful! Please log in with your new password.")
                        return redirect(url_for("login"))
                    else:
                        flash("Security answers do not match. Please try again.")
            
            except Exception as e:
                flash(f"Error: {str(e)}")

        return render_template("forgot_password.html")

    @app.route("/inbox")
    def inbox():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to access your inbox.")
            return redirect(url_for("login"))
        return render_template("inbox.html")

    @app.route("/list_car", methods=["GET", "POST"])
    def list_car():
        if request.method == "POST":
            return redirect(url_for("dashboard"))
        return render_template("list_car.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            
            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, password, role FROM users WHERE email = ?", (email,))
                    user = cursor.fetchone()
                
                if user and check_password_hash(user[1], password):
                    session = UserSession.get_instance()
                    session.login(user_id=user[0], email=email, role=user[2])
                    return redirect(url_for("dashboard"))
                else:
                    flash("Invalid email or password.")
            except Exception as e:
                flash(f"Login error: {str(e)}")
                
        return render_template("login.html")

    @app.route("/manage_cars")
    def manage_cars():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to manage your cars.")
            return redirect(url_for("login"))
        return render_template("manage_cars.html")

    @app.route("/messages/<int:user_id>")
    def message_thread(user_id):
        return render_template("message_thread.html", user_id=user_id)

    @app.route("/payment/<int:booking_id>", methods=["GET", "POST"])
    def payment(booking_id):
        if request.method == "POST":
            return redirect(url_for("payment_success"))
        return render_template("payment.html", booking_id=booking_id)

    @app.route("/payment_success")
    def payment_success():
        return render_template("payment_success.html")
    
    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to view your profile.")
            return redirect(url_for("login"))
            
        if request.method == "POST":
            return redirect(url_for("dashboard"))
        return render_template("profile.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            full_name = request.form["full_name"]
            q1 = request.form.get("security_q1", "")
            q2 = request.form.get("security_q2", "")
            q3 = request.form.get("security_q3", "")
            
            try:
                hashed_password = generate_password_hash(password)
                
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO users (email, password, security_q1, security_q2, security_q3, full_name)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (email, hashed_password, q1, q2, q3, full_name))
                    conn.commit()
                
                flash("Registration successful! Please log in.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Email already registered.")
            except Exception as e:
                flash(f"Registration error: {str(e)}")
                
        return render_template("register.html")

    @app.route("/rental_history")
    def rental_history():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to view your rental history.")
            return redirect(url_for("login"))
        return render_template("rental_history.html")

    @app.route("/review/<int:booking_id>", methods=["GET", "POST"])
    def review(booking_id):
        if request.method == "POST":
            return redirect(url_for("dashboard"))
        return render_template("review.html", booking_id=booking_id)

    @app.route("/reviews_received")
    def reviews_received():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to view reviews received.")
            return redirect(url_for("login"))
        return render_template("reviews_received.html")

    @app.route("/search")
    def search():
        return render_template("search.html")
        
    @app.route("/logout")
    def logout():
        session = UserSession.get_instance()
        session.logout()
        flash("Logged out successfully.")
        return redirect(url_for("login"))
