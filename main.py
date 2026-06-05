from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, login_url
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model
class Users(UserMixin):
    def __init__(self, username, password, email, address, city, zip, country, dob, gender, user_type, id):
        self.username = username
        self.password = password
        self.email = email
        self.address = address
        self.city = city
        self.zip = zip
        self.country = country
        self.dob = dob
        self.gender = gender
        self.user_type = user_type
        self.id = id

# Save users using JSON file
def save_users(users):
    data = {
        user.id: {
            "username": user.username,
            "password": user.password,
            "email": user.email,
            "address": user.address,
            "city": user.city,
            "zip": user.zip,
            "country": user.country,
            "dob": user.dob,
            "gender": user.gender,
            "user_type": user.user_type,
            "user_id": user.id
        } for user in users.values()
    }
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# Load users using JSON file
def load_users():
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            users = {
                id: Users(
                    user["username"], 
                    user["password"], 
                    user.get("email"), 
                    user.get("address"), 
                    user.get("city"), 
                    user.get("zip"), 
                    user.get("country"), 
                    user.get("dob"), 
                    user.get("gender"), 
                    user.get("user_type"),
                    user.get("user_id"),
                ) for id, user in data.items()
            }
            return users
    except FileNotFoundError:
        return {}
users = load_users()
# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Home route
@app.route("/")
def home():
    return render_template("home.html")

# Register route
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for("register"))
    return render_template("register.html")

# Student register route
@app.route('/student_register', methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        zip = request.form.get("zip")
        country = request.form.get("country")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        user_type = "student"
        if any(user.username == username for user in users.values()):
            return render_template("/register/student_register.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        user_id = random.randint(100000, 999999)
        if user_id in users:
            user_id = random.randint(100000, 999999)
        new_user = Users(username=username, password=hashed_password, email=email, address=address, city=city, zip=zip, country=country, dob=dob, gender=gender, user_type=user_type, id=user_id)
        users[user_id] = new_user
        save_users(users)

        return redirect(url_for("login"))
    
    return render_template("/register/student_register.html")

# Parent register route
@app.route('/parent_register', methods=["GET", "POST"])
def parent_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        zip = request.form.get("zip")
        country = request.form.get("country")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        user_type = "parent"
        if any(user.username == username for user in users.values()):
            return render_template("register/parent_register.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        user_id = random.randint(100000, 999999)
        if user_id in users:
            user_id = random.randint(100000, 999999)
        new_user = Users(username=username, password=hashed_password, email=email, address=address, city=city, zip=zip, country=country, dob=dob, gender=gender, user_type=user_type, id=user_id)
        users[user_id] = new_user
        save_users(users)

        return redirect(url_for("login"))
    
    return render_template("register/parent_register.html")

# Admin register route
@app.route('/admin_register', methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        zip = request.form.get("zip")
        country = request.form.get("country")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        user_type = "admin"
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        user_id = random.randint(100000, 999999)
        if user_id in users:
            user_id = random.randint(100000, 999999)
        new_user = Users(username=username, password=hashed_password, email=email, address=address, city=city, zip=zip, country=country, dob=dob, gender=gender, user_type=user_type, id=user_id)
        users[user_id] = new_user
        save_users(users)

        return redirect(url_for("login"))
    
    return render_template("register/admin_register.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = next((user for user in users.values() if user.username == username), None)

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("login_screen"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# Logged in route
@app.route("/login_screen")
@login_required
def login_screen():
      return render_template("login_screen.html", username=current_user.username, user_type=current_user.user_type)
# Profile route
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", username=current_user.username, user_type=current_user.user_type)
# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

#Student dashboard route
@app.route("/student_dashboard")
@login_required
def student_dashboard():
    return render_template("dashboard/student_dashboard.html", username=current_user.username)

#Parent dashboard route
@app.route("/parent_dashboard")
@login_required
def parent_dashboard():
    payment_fees = [
        {"id": 1, "name": "Tuition Fee", "amount": 500.00},
        {"id": 2, "name": "Lunch Program", "amount": 75.50},
        {"id": 3, "name": "Field Trip", "amount": 25.00},
        {"id": 4, "name": "Textbooks", "amount": 120.00},
    ] # figure out what to do with this later (involving admin dashboard)
    payment_history = [
        {"id": 1, "date": "2023-01-15", "description": "Tuition Fee - January", "amount": 500.00, "status": "Paid"},
        {"id": 2, "date": "2023-02-10", "description": "Lunch Program - February", "amount": 75.50, "status": "Paid"},
        {"id": 3, "date": "2023-03-01", "description": "Field Trip - Museum", "amount": 25.00, "status": "Paid"},
        {"id": 4, "date": "2023-04-20", "description": "Textbooks - Spring Semester", "amount": 120.00, "status": "Paid"},
        {"id": 5, "date": "2023-05-05", "description": "Graduation Fee", "amount": 150.00, "status": "Paid"},
        {"id": 6, "date": "2023-06-01", "description": "Sports Club Membership", "amount": 80.00, "status": "Paid"},
    ] # Placeholder cards to test before adding admin payments
    return render_template("dashboard/parent_dashboard.html", username=current_user.username, payment_fees=payment_fees, payment_history=payment_history)

#Admin dashboard route
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    return render_template("dashboard/admin_dashboard.html", username=current_user.username)

@app.route("/delete_user/<string:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    # Ensure only admins can delete users
    if current_user.user_type != "admin":
        return "Unauthorized: You must be an administrator to delete users.", 403

    # Prevent an admin from deleting themselves
    if current_user.id == user_id:
        return "Error: You cannot delete your own account while logged in.", 400

    if user_id in users:
        del users[user_id]
        save_users(users)
        # Redirect back to the admin dashboard or a user management page
        return redirect(url_for("admin_dashboard"))
    else:
        return "User not found.", 404


# Get all user data (admin only)
@app.route("/api/users")
@login_required
def get_users_api():
    # admin users only
    if current_user.user_type != "admin":
        return {"error": "Unauthorized access. Only admins can view this information."}, 403

    users_data_for_api = {
        user_id: {
            "username": user_obj.username,
            "id": user_obj.id,
            "email": user_obj.email,
            "user_type": user_obj.user_type,
            # You can add more fields if needed
            # IMPORTANT: Do NOT include "password" as a field! hash here for security reasons!
            # I will add connected accounts to this as well.
        } for user_id, user_obj in users.items()
    }
    return users_data_for_api, 200

@app.route("/profile/<string:user_id>")
@login_required
def user_profile(user_id):
    user_id = user_id.replace(" ", "_")
    user = users.get(user_id)
    if not user:
        return "User not found", 404
    return render_template("profile.html", user=user, user_id=user_id)

#About page route
@app.route("/about")
def about():
    return render_template("about.html")

#Contact page route
@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
   app.run(debug=True)
