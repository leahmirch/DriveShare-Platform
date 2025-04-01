from flask import render_template, request, redirect, url_for

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
        return render_template("dashboard.html")
    
    @app.route("/edit_car/<int:car_id>", methods=["GET", "POST"])
    def edit_car(car_id):
        if request.method == "POST":
            return redirect(url_for("manage_cars"))
        return render_template("edit_car.html", car_id=car_id)
    
    @app.route("/forgot_password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            return redirect(url_for("login"))
        return render_template("forgot_password.html")

    @app.route("/inbox")
    def inbox():
        return render_template("inbox.html")

    @app.route("/list_car", methods=["GET", "POST"])
    def list_car():
        if request.method == "POST":
            return redirect(url_for("dashboard"))
        return render_template("list_car.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            return redirect(url_for("home"))
        return render_template("login.html")

    @app.route("/manage_cars")
    def manage_cars():
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
        if request.method == "POST":
            return redirect(url_for("dashboard"))
        return render_template("profile.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            return redirect(url_for("home"))
        return render_template("register.html")

    @app.route("/rental_history")
    def rental_history():
        return render_template("rental_history.html")

    @app.route("/review/<int:booking_id>", methods=["GET", "POST"])
    def review(booking_id):
        if request.method == "POST":
            return redirect(url_for("dashboard"))
        return render_template("review.html", booking_id=booking_id)

    @app.route("/reviews_received")
    def reviews_received():
        return render_template("reviews_received.html")

    @app.route("/search")
    def search():
        return render_template("search.html")
