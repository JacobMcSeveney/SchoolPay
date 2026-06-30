from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, login_url
from werkzeug.security import generate_password_hash, check_password_hash
import json, random, datetime, os, uuid
from flask import flash

admin_dashboard_data = []

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
        new_user = Users(username=username, 
                         password=hashed_password, 
                         email=email, 
                         address=address, 
                         city=city, 
                         zip=zip, 
                         country=country, 
                         dob=dob, 
                         gender=gender, 
                         user_type=user_type, 
                         id=user_id)
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
        new_user = Users(username=username, 
                         password=hashed_password, 
                         email=email, 
                         address=address, 
                         city=city, 
                         zip=zip, 
                         country=country, 
                         dob=dob, 
                         gender=gender, 
                         user_type=user_type, 
                         id=user_id)
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
        new_user = Users(username=username, 
                         password=hashed_password, 
                         email=email, address=address, 
                         city=city, 
                         zip=zip, 
                         country=country, 
                         dob=dob, 
                         gender=gender, 
                         user_type=user_type, 
                         id=user_id)
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
    if current_user.user_type not in ['student', 'admin']: # Will add a 'parent_of_student' here later
        flash("Access denied. You are not a student or a parent of this student.", "error")
        return redirect(url_for('home'))
    current_date = datetime.date.today()
    payment_fees = []
    payment_history = [] # These will show the parent users payment fees and payment history

    filtered_announcements_for_student = []
    for announcement in announcements:
        if announcement.get('target_users') in ['students', 'all']:
            filtered_announcements_for_student.append(announcement)

    student_announcements = sorted(filtered_announcements_for_student, key=lambda time: datetime.datetime.strptime(time['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    for fee in payment_fees:
        fee_due_date_obj = datetime.datetime.strptime(fee["due_date"], "%m-%d-%Y").date()
        fee["due_date_obj"] = fee_due_date_obj
        fee["is_overdue"] = fee_due_date_obj < current_date and fee["status"] == "Outstanding" # Only overdue if outstanding

    return render_template("dashboard/student_dashboard.html", 
                           username=current_user.username, 
                           payment_fees=payment_fees, 
                           payment_history=payment_history, 
                           current_date=current_date, 
                           student_announcements=student_announcements)

#Parent dashboard route
@app.route("/parent_dashboard")
@login_required
def parent_dashboard():
    if current_user.user_type not in ['parent', 'admin']:
        flash("Access denied. You are not a parent.", "error")
        return redirect(url_for('home'))
    current_date = datetime.date.today()

    payment_fees = []

    user_announcement_fees = get_user_fees(current_user.id)
    for fee_data in user_announcement_fees:
        fee_entry = {
            "id": hash(fee_data.get("id")) % 100000 + 10000,
            "fee_data_id": fee_data.get("id"),
            "announcement_id": fee_data.get("announcement_id"),
            "name": fee_data.get("name", "Announcement Fee"),
            "amount": fee_data.get("amount", 0),
            "status": fee_data.get("status", "Outstanding"),
            "due_date": fee_data.get("due_date", (current_date + datetime.timedelta(days=30)).strftime("%m-%d-%Y")), # Will implement due date into the admin dashboard announcement too
            "is_announcement_fee": True
        }
        due_obj = datetime.datetime.strptime(fee_entry["due_date"], "%m-%d-%Y").date()
        fee_entry["due_date_obj"] = due_obj
        fee_entry["is_overdue"] = due_obj < current_date and fee_entry["status"] == "Outstanding"
        payment_fees.append(fee_entry)

    # Payment history
    payment_history = []
    user_id_str = str(current_user.id)
    for save in announcement_payments:
        if str(save.get("user_id")) == user_id_str:
            payment_history.append({
                "description": save.get("title", "Announcement"),
                "date": save.get("timestamp", ""),
                "amount": save.get("amount", 0),
                "status": "Completed" if save.get("type") == "free" else "Paid"
            })

    # Filter announcements for parents
    filter_parent_announcements = []
    for announcement in announcements:
        if announcement.get('target_users') in ['parents', 'all']:
            filter_parent_announcements.append(announcement)

    parent_announcements = sorted(filter_parent_announcements, key=lambda time: datetime.datetime.strptime(time['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    # Check which announcements have already been saved
    user_added_fees = {fee.get("announcement_id") for fee in user_announcement_fees}
    user_saved_free = {save.get("announcement_id") for save in announcement_payments if str(save.get("user_id")) == user_id_str}

    for fee in payment_fees:
        if not fee.get("is_announcement_fee"):
            fee_due_date_obj = datetime.datetime.strptime(fee["due_date"], "%m-%d-%Y").date()
            fee["due_date_obj"] = fee_due_date_obj
            fee["is_overdue"] = fee_due_date_obj < current_date and fee["status"] == "Outstanding" # Only overdue if outstanding

    return render_template("dashboard/parent_dashboard.html", 
                           username=current_user.username, 
                           payment_fees=payment_fees, 
                           payment_history=payment_history, 
                           current_date=current_date, 
                           parent_announcements=parent_announcements, 
                           user_added_fees=user_added_fees, 
                           user_saved_free=user_saved_free)

#Admin dashboard route
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    sort_announcements = sorted(announcements, key=lambda announcement: datetime.datetime.strptime(announcement['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    # Payment history
    all_payments = []
    for payment in announcement_payments:
        payment_user = users.get(str(payment.get("user_id")))
        payment_display = {
            "transaction_id": payment.get("transaction_id", "N/A"),
            "username": payment.get("username", payment_user.username if payment_user else "Unknown"),
            "user_id": payment.get("user_id", "N/A"),
            "title": payment.get("title", "Payment"),
            "amount": payment.get("amount", 0),
            "type": payment.get("type", "paid"),
            "card_info": payment.get("card_info", ""),
            "timestamp": payment.get("timestamp", "")
        }
        all_payments.append(payment_display)
    
    # Sort by most recent first
    all_payments.sort(key=lambda p: p["timestamp"], reverse=True)

    return render_template("dashboard/admin_dashboard.html", 
                           username=current_user.username, 
                           announcements=sort_announcements, 
                           all_payments=all_payments)

announcements_file = "announcements.json"
user_fees_file = "user_fees.json"
payment_history_file = "payments.json"

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

def save_user_fees(fees_data):
    with open(user_fees_file, "w") as f:
        json.dump(fees_data, f, indent=4)

def load_user_fees():
    if os.path.exists(user_fees_file):
        try:
            with open(user_fees_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_announcement_payments(payments_data):
    with open(payment_history_file, "w") as f:
        json.dump(payments_data, f, indent=4)

def load_announcement_payments():
    if os.path.exists(payment_history_file):
        try:
            with open(payment_history_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# Load announcements
announcements = load_announcements()
user_fees = load_user_fees()
announcement_payments = load_announcement_payments()

def get_user_fees(user_id):
    return user_fees.get(str(user_id), [])

def add_user_fee(user_id, fee_data):
    user_id_str = str(user_id)
    if user_id_str not in user_fees:
        user_fees[user_id_str] = []
    user_fees[user_id_str].append(fee_data)
    save_user_fees(user_fees)

def mark_user_fee_paid(user_id, fee_id):
    user_id_str = str(user_id)
    if user_id_str in user_fees:
        for fee in user_fees[user_id_str]:
            if str(fee.get("id")) == str(fee_id):
                fee["status"] = "Paid"
                break
        save_user_fees(user_fees)

# Route for making announcements (admin only)
@app.route("/admin/make_announcement", methods=["POST"])
@login_required
def make_announcement():
    if current_user.user_type != "admin":
        return "Unauthorized: Only administrators can make announcements.", 403

    title = request.form.get("announcement_title")
    content = request.form.get("announcement_content")
    payment_select = request.form.get("payment_select")
    payment_amount = request.form.get("announcement_payment")
    target_users = request.form.get("target_users")

    if not all([title, content, payment_select, target_users]):
        announcement_message = {"text": "All fields are required!", "type": "error"}
        return render_template("dashboard/admin_dashboard.html", 
                               username=current_user.username, 
                               announcements=announcements, 
                               announcement_message=announcement_message)


    if payment_select == "none":
        payment_type = "none"
        payment_amount_value = None
    elif payment_select == "free":
        payment_type = "free"
        payment_amount_value = None
    else:
        payment_type = "paid"
        try:
            payment_amount_value = float(payment_amount) if payment_amount else 0.0
        except (ValueError, TypeError):
            payment_amount_value = 0.0

    new_announcement = {
        "id": str(random.randint(100000, 999999)),
        "title": title,
        "content": content,
        "payment_type": payment_type,
        "payment_amount": payment_amount_value,
        "target_users": target_users,
        "sender": current_user.username,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    announcements.append(new_announcement)
    save_announcements(announcements)

    sort_announcements = sorted(announcements, key=lambda announcement: datetime.datetime.strptime(announcement['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    announcement_message = {"text": "Announcement published successfully!", "type": "success"}
    return render_template("dashboard/admin_dashboard.html", 
                           username=current_user.username, 
                           announcements=sort_announcements, 
                           announcement_message=announcement_message)


@app.route("/add_announcement_payment/<announcement_id>", methods=["POST"])
@login_required
def add_announcement_payment(announcement_id):
    if current_user.user_type not in ['parent', 'admin']:
        return "Unauthorized", 403

    # Find the announcement
    announcement = next((a for a in announcements if a["id"] == announcement_id), None)
    if not announcement:
        flash("Announcement not found.", "error")
        return redirect(url_for("parent_dashboard"))

    if announcement.get("payment_type") != "paid":
        flash("This announcement does not have a payable fee.", "error")
        return redirect(url_for("parent_dashboard"))

    # Check if already added
    existing_fees = get_user_fees(current_user.id)
    for fee in existing_fees:
        if str(fee.get("announcement_id")) == str(announcement_id):
            flash("This announcement fee has already been added to your fees.", "warning")
            return redirect(url_for("parent_dashboard"))

    # Add as a pending payment
    fee_id = str(random.randint(100000, 999999))
    new_fee = {
        "id": fee_id,
        "announcement_id": announcement_id,
        "name": announcement["title"],
        "amount": announcement.get("payment_amount", 0),
        "status": "Outstanding",
        "due_date": (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m-%d-%Y"),
        "added_on": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    add_user_fee(current_user.id, new_fee)
    flash(f"Announcement fee '{announcement['title']}' has been added to your payment fees.", "success")
    return redirect(url_for("parent_dashboard"))

@app.route("/free_announcement_payment/<announcement_id>", methods=["POST"])
@login_required
def free_announcement_payment(announcement_id):
    if current_user.user_type not in ['parent', 'admin']:
        return "Unauthorized", 403

    announcement = next((a for a in announcements if a["id"] == announcement_id), None)
    if not announcement:
        flash("Announcement not found.", "error")
        return redirect(url_for("parent_dashboard"))

    if announcement.get("payment_type") != "free":
        flash("This announcement is not a free event.", "error")
        return redirect(url_for("parent_dashboard"))

    # Check if already saved.
    for save in announcement_payments:
        if str(save.get("announcement_id")) == str(announcement_id) and str(save.get("user_id")) == str(current_user.id):
            flash("You have already saved this free announcement.", "warning")
            return redirect(url_for("parent_dashboard"))

    # Save free announcements in history
    save = {
        "id": str(random.randint(100000, 999999)),
        "announcement_id": announcement_id,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "title": announcement["title"],
        "type": "free",
        "amount": 0,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    announcement_payments.append(save)
    save_announcement_payments(announcement_payments)
    flash(f"Free announcement '{announcement['title']}' has been saved.", "success")
    return redirect(url_for("parent_dashboard"))

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
    # Admin users only
    if current_user.user_type != "admin":
        return {"error": "Unauthorized access. Only admins can view this information."}, 403

    users_data_for_api = {
        user_id: {
            "username": user_obj.username,
            "id": user_obj.id,
            "email": user_obj.email,
            "user_type": user_obj.user_type,
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
    
    # Payment history per-user (visible to admins)
    payment_history = []
    if current_user.user_type == 'admin':
        user_id_str = str(user.id)
        for save in announcement_payments:
            if str(save.get("user_id")) == user_id_str:
                payment_history.append({
                    "transaction_id": save.get("transaction_id", "N/A"),
                    "description": save.get("title", "Payment"),
                    "date": save.get("timestamp", ""),
                    "amount": save.get("amount", 0),
                    "type": save.get("type", "paid"),
                    "card_info": save.get("card_info", ""),
                    "status": "Completed" if save.get("type") == "free" else "Paid"
                })
        # Sort most recent first
        payment_history.sort(key=lambda p: p["date"], reverse=True)

    return render_template("profile.html", 
                           user=user, 
                           user_id=user_id, 
                           payment_history=payment_history)

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
@app.route("/payment/<fee_id>")
@login_required
def payment(fee_id):
    prefill_data = {}
    if fee_id:
        user_fees_list = get_user_fees(current_user.id)
        
        selected_fee = next((fee for fee in user_fees_list if str(fee.get("id")) == str(fee_id) and fee.get("status") == "Outstanding"), None)

        if selected_fee:
            prefill_data = {
                "id": current_user.id,
                "amount": selected_fee.get("amount", 0),
                "fee_name": selected_fee.get("name", "Payment"),
                "card_holder_name": current_user.username,
                "fee_id": fee_id
            }

    return render_template("payment.html", prefill_data=prefill_data)

@app.route('/make_payment', methods=['POST'])
@login_required
def make_payment():
    id = request.form.get('id')
    amount = float(request.form.get('amount'))
    card_name = request.form.get('card_holder_name')
    card_number = request.form.get('card_number')
    fee_id = request.form.get('fee_id')
    fee_name = request.form.get('fee_name', 'Payment')

    try:
        transaction_id = str(uuid.uuid4())[:12].upper()

        card_preview = f"Card Ending in {card_number[-4:]}"
        
        payment_record = {
            "transaction_id": transaction_id,
            "id": id,
            "user_id": str(current_user.id),
            "username": current_user.username,
            "title": fee_name,
            "amount": amount,
            "card_holder": card_name,
            "card_info": card_preview,
            "status": "Paid",
            "fee_id": fee_id,
            "type": "paid",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Mark the fee as paid
        if fee_id:
            mark_user_fee_paid(current_user.id, fee_id)

        admin_dashboard_data.append(payment_record)
        announcement_payments.append(payment_record)
        save_announcement_payments(announcement_payments)

        return render_template(
            'make_payment.html', 
            id=id, 
            amount=amount, 
            card_holder=card_name, 
            card_info=card_preview, 
            status="Paid", 
            timestamp=payment_record['timestamp'], 
            transaction_id=transaction_id,
            fee_name=fee_name
        )

    except Exception as e:
        return render_template('payment.html', error="Payment failed. Please try again.", prefill_data={})

if __name__ == "__main__":
   app.run(debug=True)
