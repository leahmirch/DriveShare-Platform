from flask import render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

#import scripts to use for design patterns
from python_scripts.forgot_pass_cor import PasswordRecoveryManager


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


# Builder Pattern for Car Creation
class Car:
    def __init__(self, owner_id, make, model, year, mileage, color, price, location, precise_location):
        self.owner_id = owner_id
        self.make = make
        self.model = model
        self.year = year
        self.mileage = mileage
        self.color = color
        self.price = price
        self.location = location
        self.precise_location = precise_location

class CarBuilder:
    def __init__(self):
        self._car_data = {}

    def set_owner_id(self, owner_id):
        self._car_data["owner_id"] = owner_id
        return self

    def set_make(self, make):
        self._car_data["make"] = make
        return self

    def set_model(self, model):
        self._car_data["model"] = model
        return self

    def set_year(self, year):
        self._car_data["year"] = year
        return self

    def set_mileage(self, mileage):
        self._car_data["mileage"] = mileage
        return self

    def set_color(self, color):
        self._car_data["color"] = color
        return self

    def set_price(self, price):
        self._car_data["price"] = price
        return self

    def set_location(self, location):
        self._car_data["location"] = location
        return self
    
    def set_precise_location(self, precise_location):
        self._car_data["precise_location"] = precise_location
        return self

    def build(self):
        return Car(**self._car_data)





def register_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/booking/<int:car_id>", methods=["GET", "POST"])
    def booking(car_id):
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to book a car.")
            return redirect(url_for("login"))

        car = None
        try:
            with sqlite3.connect("database.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
                car = cursor.fetchone()
                if not car:
                    flash("Car not found.")
                    return redirect(url_for("search"))
        except Exception as e:
            flash(f"Error retrieving car: {str(e)}")
            return redirect(url_for("search"))

        if request.method == "POST":
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            renter_id = UserSession.get_instance().user_id

            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")

                with sqlite3.connect("database.db") as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    # Check for conflicting bookings
                    cursor.execute('''
                        SELECT COUNT(*) FROM bookings
                        WHERE car_id = ?
                        AND (
                            (? BETWEEN start_date AND end_date) OR
                            (? BETWEEN start_date AND end_date) OR
                            (start_date BETWEEN ? AND ?) OR
                            (end_date BETWEEN ? AND ?)
                        ) AND status = 'confirmed'
                    ''', (car_id, start_date, end_date, start_date, end_date, start_date, end_date))
                    overlap = cursor.fetchone()[0]

                    if overlap > 0:
                        flash("Car is already booked for the selected dates.")
                        return render_template("booking.html", car=car)

                    # Fetch blocked (unavailable) dates for this car
                    cursor.execute('''
                        SELECT date FROM availability
                        WHERE car_id = ? AND is_available = 0
                    ''', (car_id,))
                    unavailable_rows = cursor.fetchall()
                    unavailable_dates = {row['date'] for row in unavailable_rows}

                    # Build list of all dates in this booking range
                    selected_dates = [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end_dt - start_dt).days + 1)]

                    # Check if any are blocked
                    blocked = [d for d in selected_dates if d in unavailable_dates]
                    if blocked:
                        flash(f"Car is not available on these dates: {', '.join(blocked)}")
                        return render_template("booking.html", car=car)

                    # Price and total cost
                    days = len(selected_dates)
                    total_cost = round(days * car["price"], 2)

                    cursor.execute('''
                        INSERT INTO bookings (car_id, renter_id, start_date, end_date, total_cost, status)
                        VALUES (?, ?, ?, ?, ?, 'confirmed')
                    ''', (car_id, renter_id, start_date, end_date, total_cost))
                    conn.commit()

                    print("NotifyObserver: Booking confirmed.")

                flash("Booking confirmed!")
                return redirect(url_for("dashboard"))

            except Exception as e:
                flash(f"Error during booking: {str(e)}")

        return render_template("booking.html", car=car)

    @app.route("/car/<int:car_id>")
    def car_detail(car_id):
        car = None
        try:
            with sqlite3.connect("database.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
                car = cursor.fetchone()
        except Exception as e:
            flash(f"Error retrieving car details: {str(e)}")
        return render_template("car_detail.html", car=car)

    @app.route("/dashboard")
    def dashboard():
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to access the dashboard.")
            return redirect(url_for("login"))
        return render_template("dashboard.html")
    
    @app.route("/edit_car/<int:car_id>", methods=["GET", "POST"])
    def edit_car(car_id):
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to edit your car.")
            return redirect(url_for("login"))

        if request.method == "POST":
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE cars
                    SET make = ?, model = ?, year = ?, mileage = ?, color = ?, price = ?, location = ?, precise_location = ?
                    WHERE id = ? AND owner_id = ?
                ''', (
                    request.form["make"],
                    request.form["model"],
                    int(request.form["year"]),
                    int(request.form["mileage"]),
                    request.form.get("color", ""),
                    float(request.form["price"]),
                    request.form["location"],
                    request.form.get("precise_location", ""),
                    car_id,
                    UserSession.get_instance().user_id
                ))
                conn.commit()
            flash("Car updated successfully.")
            return redirect(url_for("manage_cars"))

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cars WHERE id = ? AND owner_id = ?", (car_id, UserSession.get_instance().user_id))
            car_data = cursor.fetchone()

        if not car_data:
            flash("Car not found or you do not have permission to edit it.")
            return redirect(url_for("manage_cars"))

        car = {
            "id": car_data[0],
            "owner_id": car_data[1],
            "model": car_data[2],
            "make": car_data[3],
            "year": car_data[4],
            "mileage": car_data[5],
            "color": car_data[6],
            "price": car_data[7],
            "location": car_data[8],
            "precise_location": car_data[9]  
        }

        today = datetime.now().date()
        upcoming_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        return render_template("edit_car.html", car=car, upcoming_dates=upcoming_dates)
    
    @app.route("/forgot_password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form["email"]
            new_password = request.form["new_password"]
            input_answers = [
                request.form.get("security_q1", ""),
                request.form.get("security_q2", ""),
                request.form.get("security_q3", "")
            ]

            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT security_q1, security_q2, security_q3 FROM users WHERE email = ?", (email,))
                    user = cursor.fetchone()

                    if user:
                        recovery_manager = PasswordRecoveryManager()
                        if recovery_manager.recover_password(input_answers, list(user)):
                            hashed_password = generate_password_hash(new_password)
                            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
                            conn.commit()
                            flash("Password reset successful. Please log in.")
                            return redirect(url_for("login"))
                        else:
                            flash("Security answers do not match. Try again.")
                    else:
                        flash("No user found with that email.")

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
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in to list a car.")
            return redirect(url_for("login"))

        if request.method == "POST":
            required_fields = ["make", "model", "year", "mileage", "price", "location"]
            for field in required_fields:
                if not request.form.get(field):
                    flash(f"Field '{field}' is required.")
                    return redirect(url_for("list_car"))

            builder = CarBuilder()
            car = builder.set_owner_id(UserSession.get_instance().user_id) \
                        .set_make(request.form["make"]) \
                        .set_model(request.form["model"]) \
                        .set_year(int(request.form["year"])) \
                        .set_mileage(int(request.form["mileage"])) \
                        .set_color(request.form.get("color", "")) \
                        .set_price(float(request.form["price"])) \
                        .set_location(request.form["location"]) \
                        .set_precise_location(request.form["precise_location"]) \
                        .build()

            precise_location = request.form.get("precise_location", "")

            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO cars (owner_id, make, model, year, mileage, color, price, location, precise_location, image_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        car.owner_id,
                        car.make,
                        car.model,
                        car.year,
                        car.mileage,
                        car.color,
                        car.price,
                        car.location,
                        car.precise_location,
                        None
                    ))
                    conn.commit()

                flash("Car listed successfully.")
                return redirect(url_for("dashboard"))

            except Exception as e:
                flash(f"Error listing car: {str(e)}")
                return redirect(url_for("list_car"))

        return render_template("list_car.html")
    
    from flask import jsonify

    @app.route("/availability/<int:car_id>")
    def view_availability(car_id):
        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT date, is_available
                    FROM availability
                    WHERE car_id = ?
                    ORDER BY date
                """, (car_id,))
                availability = cursor.fetchall()
                data = [{"date": row[0], "is_available": bool(row[1])} for row in availability]
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/set_availability/<int:car_id>", methods=["POST"])
    def set_availability(car_id):
        if not UserSession.get_instance().is_authenticated():
            flash("Login required.")
            return redirect(url_for("login"))

        user_id = UserSession.get_instance().user_id

        # Get dates from the new text input
        unavailable_raw = request.form.get("unavailable_dates", "")
        unavailable_dates = [d.strip() for d in unavailable_raw.split(",") if d.strip()]

        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()

                # Verify ownership
                cursor.execute("SELECT owner_id FROM cars WHERE id = ?", (car_id,))
                result = cursor.fetchone()
                if not result or result[0] != user_id:
                    flash("Unauthorized.")
                    return redirect(url_for("dashboard"))

                # Delete only the specific dates being updated (clean slate approach optional)
                for date in unavailable_dates:
                    cursor.execute(
                        "REPLACE INTO availability (car_id, date, is_available) VALUES (?, ?, 0)",
                        (car_id, date)
                    )

                conn.commit()
                flash("Unavailable dates saved.")
        except Exception as e:
            flash(f"Error: {str(e)}")

        return redirect(url_for("edit_car", car_id=car_id))

    @app.route("/delete_car/<int:car_id>", methods=["POST", "GET"])
    def delete_car(car_id):
        if not UserSession.get_instance().is_authenticated():
            flash("Please log in.")
            return redirect(url_for("login"))

        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
                conn.commit()
            flash("Car deleted successfully.")
        except Exception as e:
            flash(f"Error deleting car: {str(e)}")
        
        return redirect(url_for("manage_cars"))

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

        user_id = UserSession.get_instance().user_id
        with sqlite3.connect("database.db") as conn:
            conn.row_factory = sqlite3.Row
            cars = conn.execute("SELECT * FROM cars WHERE owner_id = ?", (user_id,)).fetchall()

        return render_template("manage_cars.html", cars=cars)

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

        user_id = UserSession.get_instance().user_id
        rented_cars = []
        your_listings = []

        try:
            with sqlite3.connect("database.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Rentals made by this user
                cursor.execute('''
                    SELECT b.start_date, b.end_date, c.make, c.model, c.location
                    FROM bookings b
                    JOIN cars c ON b.car_id = c.id
                    WHERE b.renter_id = ?
                    ORDER BY b.start_date DESC
                ''', (user_id,))
                rented_cars = cursor.fetchall()

                # Bookings on this user's listed cars
                cursor.execute('''
                    SELECT b.start_date, b.end_date, u.full_name AS renter_name, c.make, c.model
                    FROM bookings b
                    JOIN cars c ON b.car_id = c.id
                    JOIN users u ON b.renter_id = u.id
                    WHERE c.owner_id = ?
                ''', (user_id,))
                your_listings = cursor.fetchall()

        except Exception as e:
            flash(f"Could not retrieve rental history: {str(e)}")

        return render_template("rental_history.html", rented_cars=rented_cars, your_listings=your_listings)

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
        location = request.args.get("location", "").strip()
        date = request.args.get("date", "").strip()
        make = request.args.get("make", "").strip()
        color = request.args.get("color", "").strip()
        min_price = request.args.get("min_price", "").strip()
        max_price = request.args.get("max_price", "").strip()

        cars = []
        try:
            query = '''
                SELECT * FROM cars
                WHERE is_available = 1
                AND LOWER(location) LIKE LOWER(?)
                AND id NOT IN (
                    SELECT car_id FROM bookings
                    WHERE ? BETWEEN start_date AND end_date AND status = 'confirmed'
                )
                AND id NOT IN (
                    SELECT car_id FROM availability
                    WHERE date = ? AND is_available = 0
                )
            '''
            params = [f"%{location}%", date, date]

            if make:
                query += " AND LOWER(make) LIKE LOWER(?)"
                params.append(f"%{make}%")
            if color:
                query += " AND LOWER(color) LIKE LOWER(?)"
                params.append(f"%{color}%")
            if min_price:
                query += " AND price >= ?"
                params.append(float(min_price))
            if max_price:
                query += " AND price <= ?"
                params.append(float(max_price))

            with sqlite3.connect("database.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                cars = cursor.fetchall()

        except Exception as e:
            flash(f"Search error: {str(e)}")

        return render_template(
            "search.html",
            cars=cars,
            location=location,
            date=date,
            make=make,
            color=color,
            min_price=min_price,
            max_price=max_price
        )

    @app.route("/logout")
    def logout():
        session = UserSession.get_instance()
        session.logout()
        flash("Logged out successfully.")
        return redirect(url_for("login"))
