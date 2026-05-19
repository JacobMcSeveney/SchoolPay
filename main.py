from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json

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
            "user_type": user.user_type
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
                    id
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

        user_id = username
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

        user_id = username
        new_user = Users(username=username, password=hashed_password, email=email, address=address, city=city, zip=zip, country=country, dob=dob, gender=gender, user_type=user_type, id=user_id)
        users[user_id] = new_user
        save_users(users)

        return redirect(url_for("login"))
    
    return render_template("register/parent_register.html")

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
    payment_fees = [] # figure out what to do with this later
    return render_template("dashboard/parent_dashboard.html", username=current_user.username, payment_fees=payment_fees)

#Admin dashboard route
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    return render_template("dashboard/admin_dashboard.html", username=current_user.username)

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
