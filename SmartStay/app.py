import os
import sqlite3
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
DATABASE = os.path.join(app.root_path, "smartstay.db")

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()

def init_db():
    con = sqlite3.connect(DATABASE)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    );
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        address TEXT NOT NULL,
        price REAL NOT NULL,
        rating REAL NOT NULL,
        amenities TEXT NOT NULL,
        description TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS cabs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cab_type TEXT NOT NULL,
        price_per_km REAL NOT NULL,
        rating REAL NOT NULL,
        seats INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        booking_type TEXT NOT NULL,
        item_name TEXT NOT NULL,
        details TEXT NOT NULL,
        total_price REAL NOT NULL,
        booking_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Confirmed',
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    count = con.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]
    if count == 0:
        con.executemany("""INSERT INTO hotels
            (name,city,address,price,rating,amenities,description)
            VALUES (?,?,?,?,?,?,?)""", [
            ("The Grand Residency", "Lucknow", "Hazratganj, Lucknow", 2800, 4.5, "Wi-Fi, Breakfast, Parking", "Comfortable city hotel close to shopping and dining."),
            ("River View Inn", "Lucknow", "Gomti Nagar, Lucknow", 2200, 4.2, "Wi-Fi, Restaurant, AC", "Modern rooms with easy access to the city."),
            ("City Comfort Hotel", "Delhi", "Karol Bagh, Delhi", 1900, 4.0, "Wi-Fi, AC, Room Service", "Affordable stay for business and leisure."),
            ("Maple Suites", "Jaipur", "MI Road, Jaipur", 3200, 4.6, "Wi-Fi, Pool, Breakfast", "Well-equipped suites in a convenient location.")
        ])
        con.executemany("""INSERT INTO cabs (name,cab_type,price_per_km,rating,seats)
            VALUES (?,?,?,?,?)""", [
            ("Swift Ride", "Mini", 12, 4.2, 4),
            ("Comfort Sedan", "Sedan", 15, 4.5, 4),
            ("Family Traveller", "SUV", 20, 4.7, 6),
            ("Premium Drive", "Premium", 25, 4.8, 4)
        ])
    admin = con.execute("SELECT id FROM users WHERE email=?", ("admin@smartstay.com",)).fetchone()
    if not admin:
        con.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                    ("SmartStay Admin", "admin@smartstay.com",
                     generate_password_hash("Admin@123"), "admin"))
    con.commit()
    con.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter all details. Password must be at least 6 characters.", "danger")
            return render_template("register.html")
        try:
            db().execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                         (name, email, generate_password_hash(password)))
            db().commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("This email is already registered.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("admin") if user["role"] == "admin" else url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/hotels")
def hotels():
    city = request.args.get("city", "").strip()
    sort = request.args.get("sort", "price")
    query = "SELECT * FROM hotels"
    params = []
    if city:
        query += " WHERE city LIKE ?"
        params.append(f"%{city}%")
    query += " ORDER BY " + ("rating DESC" if sort == "rating" else "price ASC")
    rows = db().execute(query, params).fetchall()
    return render_template("hotels.html", hotels=rows, city=city, sort=sort)

@app.route("/cabs", methods=["GET", "POST"])
def cabs():
    distance = request.values.get("distance", "10")
    try:
        distance_num = float(distance)
        if distance_num <= 0 or distance_num > 2000:
            raise ValueError
    except ValueError:
        distance_num = 10
        flash("Enter a valid distance between 1 and 2000 km.", "warning")
    rows = db().execute("SELECT * FROM cabs ORDER BY price_per_km ASC").fetchall()
    cab_quotes = [{"cab": row, "fare": round(row["price_per_km"] * distance_num, 2)} for row in rows]
    return render_template("cabs.html", cab_quotes=cab_quotes, distance=distance_num)

@app.route("/book/hotel/<int:hotel_id>", methods=["GET", "POST"])
@login_required
def book_hotel(hotel_id):
    hotel = db().execute("SELECT * FROM hotels WHERE id=?", (hotel_id,)).fetchone()
    if not hotel:
        flash("Hotel not found.", "danger")
        return redirect(url_for("hotels"))
    if request.method == "POST":
        checkin = request.form.get("checkin")
        checkout = request.form.get("checkout")
        guests = request.form.get("guests", "1")
        try:
            start = datetime.strptime(checkin, "%Y-%m-%d").date()
            end = datetime.strptime(checkout, "%Y-%m-%d").date()
            guests_num = int(guests)
            nights = (end - start).days
            if nights <= 0 or guests_num < 1 or guests_num > 10:
                raise ValueError
        except (ValueError, TypeError):
            flash("Choose valid dates (checkout after check-in) and 1–10 guests.", "danger")
            return render_template("book_hotel.html", hotel=hotel)
        total = hotel["price"] * nights
        details = f"City: {hotel['city']} | Check-in: {checkin} | Check-out: {checkout} | Nights: {nights} | Guests: {guests_num}"
        db().execute("""INSERT INTO bookings(user_id,booking_type,item_name,details,total_price,booking_date)
                        VALUES(?,?,?,?,?,?)""",
                     (session["user_id"], "Hotel", hotel["name"], details, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
        db().commit()
        flash(f"Hotel booking confirmed. Total: ₹{total:.2f}", "success")
        return redirect(url_for("dashboard"))
    return render_template("book_hotel.html", hotel=hotel)

@app.route("/book/cab/<int:cab_id>", methods=["GET", "POST"])
@login_required
def book_cab(cab_id):
    cab = db().execute("SELECT * FROM cabs WHERE id=?", (cab_id,)).fetchone()
    if not cab:
        flash("Cab not found.", "danger")
        return redirect(url_for("cabs"))
    if request.method == "POST":
        pickup = request.form.get("pickup", "").strip()
        drop = request.form.get("drop", "").strip()
        try:
            distance = float(request.form.get("distance", "0"))
            if not pickup or not drop or distance <= 0 or distance > 2000:
                raise ValueError
        except ValueError:
            flash("Enter pickup, drop and a valid distance.", "danger")
            return render_template("book_cab.html", cab=cab)
        total = round(cab["price_per_km"] * distance, 2)
        details = f"Pickup: {pickup} | Drop: {drop} | Distance: {distance} km"
        db().execute("""INSERT INTO bookings(user_id,booking_type,item_name,details,total_price,booking_date)
                        VALUES(?,?,?,?,?,?)""",
                     (session["user_id"], "Cab", cab["name"], details, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
        db().commit()
        flash(f"Cab booking confirmed. Estimated fare: ₹{total:.2f}", "success")
        return redirect(url_for("dashboard"))
    return render_template("book_cab.html", cab=cab)

@app.route("/dashboard")
@login_required
def dashboard():
    bookings = db().execute("SELECT * FROM bookings WHERE user_id=? ORDER BY id DESC",
                            (session["user_id"],)).fetchall()
    return render_template("dashboard.html", bookings=bookings)

@app.route("/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    db().execute("""UPDATE bookings SET status='Cancelled'
                    WHERE id=? AND user_id=? AND status='Confirmed'""",
                 (booking_id, session["user_id"]))
    db().commit()
    flash("Booking status updated.", "success")
    return redirect(url_for("dashboard"))

@app.route("/admin")
@admin_required
def admin():
    hotels = db().execute("SELECT * FROM hotels ORDER BY id DESC").fetchall()
    cabs = db().execute("SELECT * FROM cabs ORDER BY id DESC").fetchall()
    bookings = db().execute("""SELECT bookings.*, users.name AS customer
                               FROM bookings JOIN users ON users.id=bookings.user_id
                               ORDER BY bookings.id DESC""").fetchall()
    return render_template("admin.html", hotels=hotels, cabs=cabs, bookings=bookings)

@app.route("/admin/hotel/add", methods=["POST"])
@admin_required
def add_hotel():
    try:
        values = (request.form["name"].strip(), request.form["city"].strip(),
                  request.form["address"].strip(), float(request.form["price"]),
                  float(request.form["rating"]), request.form["amenities"].strip(),
                  request.form["description"].strip())
        if not all([values[0], values[1], values[2]]) or values[3] <= 0 or not 0 <= values[4] <= 5:
            raise ValueError
        db().execute("""INSERT INTO hotels(name,city,address,price,rating,amenities,description)
                        VALUES(?,?,?,?,?,?,?)""", values)
        db().commit()
        flash("Hotel added.", "success")
    except (ValueError, KeyError):
        flash("Please enter valid hotel details.", "danger")
    return redirect(url_for("admin"))

@app.route("/admin/cab/add", methods=["POST"])
@admin_required
def add_cab():
    try:
        values = (request.form["name"].strip(), request.form["cab_type"].strip(),
                  float(request.form["price_per_km"]), float(request.form["rating"]),
                  int(request.form["seats"]))
        if not values[0] or values[2] <= 0 or not 0 <= values[3] <= 5 or values[4] < 1:
            raise ValueError
        db().execute("INSERT INTO cabs(name,cab_type,price_per_km,rating,seats) VALUES(?,?,?,?,?)", values)
        db().commit()
        flash("Cab added.", "success")
    except (ValueError, KeyError):
        flash("Please enter valid cab details.", "danger")
    return redirect(url_for("admin"))

@app.route("/admin/hotel/delete/<int:item_id>", methods=["POST"])
@admin_required
def delete_hotel(item_id):
    db().execute("DELETE FROM hotels WHERE id=?", (item_id,))
    db().commit()
    flash("Hotel deleted.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/cab/delete/<int:item_id>", methods=["POST"])
@admin_required
def delete_cab(item_id):
    db().execute("DELETE FROM cabs WHERE id=?", (item_id,))
    db().commit()
    flash("Cab deleted.", "success")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
