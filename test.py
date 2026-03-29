import json
import re
import random

#Username and Password Login
Log = input("If you want to make an account, enter 1, if you want to login, enter 2: ")
def load_accounts():
    """Loads accounts from the JSON file, initializing parent and student sections if they don't exist."""
    try:
        with open("account.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"parents": {}, "students": {}}  # Initialize with parent and student sections
    
    if "parents" not in data:
        data["parents"] = {}
    if "students" not in data:
        data["students"] = {}
    
    return data

def save_accounts(data):
    with open("account.json", "w") as f:
        json.dump(data, f, indent=4)
def connect_accounts(userclass, username, password, code):
    if userclass == "1":
        students = int(input("How many students do you want to connect? Enter a number: "))
        with open("account.json", "r") as f:
            data = json.load(f)

        if username not in data or data[username].get("userclass") != "Parent":
            data[username] = {
                "password": password,
                "userclass": "Parent",
                "code": code,
                "students": []
            }
        for i in range(students):
            studentuser = input("Enter the username of the student: ")
            studentcode = int(input("Enter the students code: "))

            if studentuser in data and studentcode == data[studentuser]["code"]:
                verify = input("Are you sure you want to connect ", studentuser, "to your account? Enter y or n: ")
                if verify == "y":
                    if studentuser not in data[username]["students"]:
                        data[username]["students"].append(studentuser)
                    print(username, "has been connected as a parent of", studentuser)
                elif verify == "n":
                    print("Connection cancelled")
                else:
                    print("Invalid input, please input y or n")
            else:
                print("Invalid username or code, not found in system")
        with open("account.json", "w") as f:
            json.dump(data, f, indent=4)

if Log == "1":

    username = input("Enter a username: ")
    with open("account.json", "r") as f:
        data = json.load(f)
        if username in data:
            print("Username already exists")
            exit()
    password = input("Enter a password: ")
    SpecialSym = ['$', '@', '#', '%', '!', '*']
    val = True

    if len(password) < 6:
        print('Password length should be at least 6')
        val = False
        exit()
    if len(password) > 20:
        print('Length should not be greater than 20')
        val = False
        exit()

    # Flags for each condition
    has_digit = has_upper = has_lower = has_sym = False

    for char in password:
        if 48 <= ord(char) <= 57:
            has_digit = True
        elif 65 <= ord(char) <= 90:
            has_upper = True
        elif 97 <= ord(char) <= 122:
            has_lower = True
        elif char in SpecialSym:
            has_sym = True

    if not has_digit:
        print('Password should have at least one numeral')
        val = False
        exit()
    if not has_upper:
        print('Password should have at least one uppercase letter')
        val = False
        exit()
    if not has_lower:
        print('Password should have at least one lowercase letter')
        val = False
        exit()
    if not has_sym:
        print('Password should have at least one of the symbols !$@#%*')
        val = False
        exit()

    code = random.randint(1000, 9999)
    for i in range(code):   
        if code in data["students"] or code in data["parents"]:
            code = random.randint(1000, 9999)
        else:
            break
    data = load_accounts()
    account = {
        "username": username,
        "password": password,
        "code": code
    }
    #Connect Accounts
    userclass = input("Are you a parent or a student? Enter 1 for parent, 2 for student: ")
    if userclass == "1":
        connect_accounts(userclass, username, password, code)
    elif userclass == "2":
            data = load_accounts()
            data["students"][username] = {
                "password": password,
                "userclass": "Student",
                "code": code
            }
            save_accounts(data)
            print(username, "has been created as a student! Your code is", code, "use this to connect your account with your parents!")
    else:
        print("Invalid input, please input 1 or 2")
elif Log == "2":
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    with open("account.json", "r") as f:
        data = json.load(f)
    if username in data and password == data[username]["password"]:
        usertype = data[username]["userclass"]
        print(username, "has logged into", usertype, "account")
    else:
        print("Invalid username or password")
    if usertype == "Parent":
        with open("account.json", "r") as f:
            data = json.load(f)
        parentactions = int(input("What would you like to do? Enter 1 to connect new student account. Enter 2 to log out "))
        if parentactions == 1:
            connect_accounts("1", username, password, data[username].get("code"))
        elif parentactions == 2:
            print("Logged out")
        else:
            print("Invalid input, please input 1 or 2")
else:
    print("Invalid input, please input 1 or 2")









from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model
class Users(UserMixin):
    id = None
    def __init__(self, username, password, id):
            self.username = username
            self.password = password
            self.id = id
# Load users from JSON file
def load_users():
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            users = {id: Users(user["username"], user["password"], id) for id, user in data.items()}
            return users
    except FileNotFoundError:
        return {}

# Save users to JSON file
def save_users(users):
    data = {user.id: {"username": user.username, "password": user.password} for user in users.values()}
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# Create database
with app.app_context():
    pass
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
        username = request.form.get("username")
        password = request.form.get("password")

        if any(user.username == username for user in users.values()):
            return render_template("sign_up.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        user_id = str(len(users) + 1)
        new_user = Users(username=username, password=hashed_password, id=user_id)
        users[user_id] = new_user
        save_users(users)

        return redirect(url_for("login"))
    
    return render_template("sign_up.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = next((user for user in users.values() if user.username == username), None)

        if user and check_password_hash(user.password, password):
            login_user(user) #type: ignore
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# Protected dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
   app.run(debug=True)
