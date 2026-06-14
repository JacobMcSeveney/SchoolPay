from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, login_url
from werkzeug.security import generate_password_hash, check_password_hash
import json, random, datetime, os
from flask import flash

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
    if current_user.user_type not in ['student', 'admin']: #will add a 'parent_of_student' here later
        flash("Access denied. You are not a student or a parent of this student.", "error")
        return redirect(url_for('home'))
    payment_fees = [
        {"id": 1, "name": "Tuition Fee", "amount": 500.00, "status": "Outstanding", "due_date": "8-23-2026"}
    ] # figure out what to do with this later (involving admin dashboard)
    payment_history = []

    filtered_announcements_for_student = []
    for announcement in announcements:
        if announcement.get('target_users') in ['students', 'all']:
            filtered_announcements_for_student.append(announcement)

    student_announcements = sorted(filtered_announcements_for_student, key=lambda time: datetime.datetime.strptime(time['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    for fee in payment_fees:
        fee_due_date_obj = datetime.datetime.strptime(fee["due_date"], "%m-%d-%Y").date()
        fee["due_date_obj"] = fee_due_date_obj
        fee["is_overdue"] = fee_due_date_obj < current_date and fee["status"] == "Outstanding" # Only overdue if outstanding

    return render_template("dashboard/student_dashboard.html", username=current_user.username, payment_fees=payment_fees, payment_history=payment_history, current_date=current_date, student_announcements=student_announcements)

#Parent dashboard route
@app.route("/parent_dashboard")
@login_required
def parent_dashboard():
    if current_user.user_type not in ['parent', 'admin']:
        flash("Access denied. You are not a parent.", "error")
        return redirect(url_for('home'))
    payment_fees = [
        {"id": 1, "name": "Tuition Fee", "amount": 500.00, "status": "Outstanding", "due_date": "8-23-2026"}
    ] # figure out what to do with this later (involving admin dashboard)
    payment_history = []
    current_date = datetime.date.today()
    filtered_announcements_for_parent = []
    for announcement in announcements:
        if announcement.get('target_users') in ['parents', 'all']:
            filtered_announcements_for_parent.append(announcement)

    parent_announcements = sorted(filtered_announcements_for_parent, key=lambda time: datetime.datetime.strptime(time['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    for fee in payment_fees:
        fee_due_date_obj = datetime.datetime.strptime(fee["due_date"], "%m-%d-%Y").date()
        fee["due_date_obj"] = fee_due_date_obj
        fee["is_overdue"] = fee_due_date_obj < current_date and fee["status"] == "Outstanding" # Only overdue if outstanding
    return render_template("dashboard/parent_dashboard.html", username=current_user.username, payment_fees=payment_fees, payment_history=payment_history, current_date=current_date, parent_announcements=parent_announcements)

#Admin dashboard route
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    sort_announcements = sorted(announcements, key=lambda announcement: datetime.datetime.strptime(announcement['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    return render_template("dashboard/admin_dashboard.html", username=current_user.username, announcements=sort_announcements)

announcements_file = "announcements.json"

def save_announcements(announcements_data):
    with open(announcements_file, "w") as f:
        json.dump(announcements_data, f, indent=4)

def load_announcements():
    if os.path.exists(announcements_file):
        try:
            with open(announcements_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# Load announcements
announcements = load_announcements()
# Route for making announcements (admin only)
@app.route("/admin/make_announcement", methods=["POST"])
@login_required
def make_announcement():
    if current_user.user_type != "admin":
        return "Unauthorized: Only administrators can make announcements.", 403

    title = request.form.get("announcement_title")
    content = request.form.get("announcement_content")
    payment = request.form.get("announcement_payment")
    target_users = request.form.get("target_users")

    if not all([title, content, payment, target_users]):
        announcement_message = {"text": "An Error Occurred!", "type": "error"}
        return render_template("dashboard/admin_dashboard.html", username=current_user.username, announcements=announcements, announcement_message=announcement_message)

    new_announcement = {
        "id": str(random.randint(100000, 999999)),
        "title": title,
        "content": content,
        "payment": payment,
        "target_users": target_users,
        "sender": current_user.username,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    announcements.append(new_announcement)
    save_announcements(announcements)

    sort_announcements = sorted(announcements, key=lambda announcement: datetime.datetime.strptime(announcement['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    announcement_message = {"text": "Announcement published successfully!", "type": "success"}
    return render_template("dashboard/admin_dashboard.html", username=current_user.username, announcements=sort_announcements, announcement_message=announcement_message)

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
        # Redirect back to the admin dashboard
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
            # IMPORTANT: Do NOT include "password" as a field!
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

#Payment route
@app.route("/payment", defaults={'fee_id': None})
@app.route("/payment/<int:fee_id>")
@login_required
def payment(fee_id):
    prefill_data = {}
    if fee_id:
        all_possible_fees = [
            {"id": 1, "name": "Tuition Fee", "amount": 500.00, "status": "Outstanding", "due_date": "12-25-2024"},
            {"id": 2, "name": "Textbook Fee", "amount": 75.50, "status": "Outstanding", "due_date": "01-15-2023"},
            {"id": 3, "name": "Activity Fund", "amount": 25.00, "status": "Outstanding", "due_date": "10-01-2023"}
        ]
        
        selected_fee = next((fee for fee in all_possible_fees if fee["id"] == fee_id and fee["status"] == "Outstanding"), None)

        if selected_fee:
            prefill_data = {
                "student_id": current_user.username,
                "amount": selected_fee["amount"],
                "fee_name": selected_fee["name"]
            }
        else:
            pass

    return render_template("payment.html", prefill_data=prefill_data)

if __name__ == "__main__":
   app.run(debug=True)
