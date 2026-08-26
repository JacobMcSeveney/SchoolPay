import datetime
import json
import os
import random
import uuid

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

teacher_dashboard_data = []

MIN_ID = 100000
MAX_ID = 999999
FEE_DUE_DAYS = 30  # Default number of days until a fee is due
current_year = datetime.datetime.now().year

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# User model
class Users(UserMixin):
    def __init__(
        self,
        username,
        password,
        email,
        address,
        city,
        postcode,
        country,
        dob,
        gender,
        user_type,
        id,
    ):
        self.username = username
        self.password = password
        self.email = email
        self.address = address
        self.city = city
        self.postcode = postcode
        self.country = country
        self.dob = dob
        self.gender = gender
        self.user_type = user_type
        self.id = str(id)


# Save users using JSON file
def save_users(users):
    data = {
        str(user.id): {
            "username": user.username,
            "password": user.password,
            "email": user.email,
            "address": user.address,
            "city": user.city,
            "postcode": user.postcode,
            "country": user.country,
            "dob": user.dob,
            "gender": user.gender,
            "user_type": user.user_type,
            "user_id": str(user.id),
        }
        for user in users.values()
    }
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)


# Load users using JSON file
def load_users():
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            users = {
                str(id): Users(
                    user["username"],
                    user["password"],
                    user.get("email"),
                    user.get("address"),
                    user.get("city"),
                    user.get("postcode"),
                    user.get("country"),
                    user.get("dob"),
                    user.get("gender"),
                    user.get("user_type"),
                    user.get("user_id", id),
                )
                for id, user in data.items()
            }
            return users
    except FileNotFoundError:
        return {}


users = load_users()


# Checks if the dob is valid.
def validate_dob(dob):
    if not dob:
        return False, "Date of birth is required."

    try:
        selected_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        return False, "Please enter a valid date of birth."

    min_date = datetime.date(1900, 1, 1)
    max_date = datetime.date.today()

    if selected_date < min_date or selected_date > max_date:
        min_str = min_date.strftime("%Y-%m-%d")
        max_str = max_date.strftime("%Y-%m-%d")
        return (
            False,
            f"Date of birth must be between {min_str} and {max_str}.",
        )

    return True, ""


# Checks if the email is valid.
def validate_email(email):
    if not email:
        return False, "Email is required."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    return True, ""


# Checks if the password is valid.
def validate_password(password):
    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


# Checks if the username is valid.
def validate_username(username):
    if not username:
        return False, "Username is required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if any(user.username == username for user in users.values()):
        return False, "Username already taken."
    return True, ""


# Checks that the postcode contains digits only.
def validate_postcode(postcode):
    if not postcode:
        return False, "Post code is required."
    if not postcode.isascii() or not postcode.isdigit():
        return False, "Post code must contain numbers only."
    return True, ""


# Checks all the form values.
def validate_registration_form(data):
    validators = [
        validate_username(data.get("username")),
        validate_password(data.get("password")),
        validate_email(data.get("email")),
        validate_postcode(data.get("postcode")),
        validate_dob(data.get("dob")),
    ]

    for is_valid, error in validators:
        if not is_valid:
            return False, error
    return True, ""


# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(str(user_id))


# Home route
@app.route("/")
def home():
    return render_template("home.html")


# Account register route
@app.route("/register", methods=["GET", "POST"])
def register():
    today = datetime.date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")
        address = request.form.get("address")
        city = request.form.get("city")
        postcode = request.form.get("postcode")
        country = request.form.get("country")
        dob_day = request.form.get("dob_day")
        dob_month = request.form.get("dob_month")
        dob_year = request.form.get("dob_year")
        dob = f"{dob_year}-{dob_month}-{dob_day}" if all((dob_year, dob_month, dob_day)) else ""
        gender = request.form.get("gender")
        user_type = request.form.get("user_type")

        # Run all field validators.
        registration_data = request.form.to_dict()
        registration_data["dob"] = dob
        is_valid, error = validate_registration_form(registration_data)
        if not is_valid:
            return render_template("register.html", error=error, today=today)

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match!", today=today)

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        while True:
            user_id = str(random.randint(MIN_ID, MAX_ID))
            if user_id not in users:
                break
        new_user = Users(
            username=username,
            password=hashed_password,
            email=email,
            address=address,
            city=city,
            postcode=postcode,
            country=country,
            dob=dob,
            gender=gender,
            user_type=user_type,
            id=user_id,
        )
        users[user_id] = new_user
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html", today=today)


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
    return render_template(
        "login_screen.html", username=current_user.username, user_type=current_user.user_type
    )


# Profile route
@app.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html", username=current_user.username, user_type=current_user.user_type
    )


# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# Student dashboard route
@app.route("/student_dashboard")
@login_required
def student_dashboard():
    if current_user.user_type not in [
        "student",
        "teacher",
    ]:  # Will add a 'parent_of_student' here later
        flash("Access denied. You are not a student or a parent of this student.", "error")
        return redirect(url_for("home"))
    # Shared with any connected parent accounts to the student accounts
    payment_history = get_combined_payment_history(current_user.id)

    # Connected accounts
    user_connections = get_connected_accounts(current_user.id)

    filtered_announcements_for_student = []
    for announcement in announcements:
        if announcement.get("status") == "cancelled":
            continue
        if announcement.get("target_users") in ["students", "all"]:
            filtered_announcements_for_student.append(announcement)

    student_announcements = sorted(
        filtered_announcements_for_student,
        key=lambda time: datetime.datetime.strptime(time["timestamp"], "%Y-%m-%d %H:%M:%S"),
        reverse=True,
    )

    user_notifications = get_user_notifications(current_user.id)
    unread_notification_count = get_unread_notification_count(current_user.id)

    return render_template(
        "dashboard/student_dashboard.html",
        username=current_user.username,
        user_id=current_user.id,
        user_type=current_user.user_type,
        payment_history=payment_history,
        student_announcements=student_announcements,
        notifications=user_notifications,
        unread_count=unread_notification_count,
        user_connections=user_connections,
    )


# Parent dashboard route
@app.route("/parent_dashboard")
@login_required
def parent_dashboard():
    if current_user.user_type not in ["parent", "teacher"]:
        flash("Access denied. You are not a parent.", "error")
        return redirect(url_for("home"))
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
            "due_date": fee_data.get(
                "due_date",
                (current_date + datetime.timedelta(days=FEE_DUE_DAYS)).strftime("%m-%d-%Y"),
            ),
            "is_announcement_fee": True,
        }
        due_obj = datetime.datetime.strptime(fee_entry["due_date"], "%m-%d-%Y").date()
        fee_entry["due_date_obj"] = due_obj
        fee_entry["is_overdue"] = due_obj < current_date and fee_entry["status"] == "Outstanding"
        payment_fees.append(fee_entry)

    # Payment history (shared with connected student accounts)
    user_id_str = str(current_user.id)
    payment_history = get_combined_payment_history(current_user.id)

    # Connected accounts
    user_connections = get_connected_accounts(current_user.id)

    # Filter announcements for parents
    filter_parent_announcements = []
    for announcement in announcements:
        if announcement.get("status") == "cancelled":
            continue
        if announcement.get("target_users") in ["parents", "all"]:
            filter_parent_announcements.append(announcement)

    parent_announcements = sorted(
        filter_parent_announcements,
        key=lambda time: datetime.datetime.strptime(time["timestamp"], "%Y-%m-%d %H:%M:%S"),
        reverse=True,
    )

    # Check which announcements have already been saved
    user_added_fees = {fee.get("announcement_id") for fee in user_announcement_fees}
    user_saved_free = {
        save.get("announcement_id")
        for save in announcement_payments
        if str(save.get("user_id")) == user_id_str
    }

    for fee in payment_fees:
        if not fee.get("is_announcement_fee"):
            fee_due_date_obj = datetime.datetime.strptime(fee["due_date"], "%d-%m-%Y").date()
            fee["due_date_obj"] = fee_due_date_obj
            fee["is_overdue"] = (
                fee_due_date_obj < current_date and fee["status"] == "Outstanding"
            )  # Only overdue if outstanding

    user_notifications = get_user_notifications(current_user.id)
    unread_notification_count = get_unread_notification_count(current_user.id)

    return render_template(
        "dashboard/parent_dashboard.html",
        username=current_user.username,
        user_id=current_user.id,
        user_type=current_user.user_type,
        payment_fees=payment_fees,
        payment_history=payment_history,
        current_date=current_date,
        parent_announcements=parent_announcements,
        user_added_fees=user_added_fees,
        user_saved_free=user_saved_free,
        notifications=user_notifications,
        unread_count=unread_notification_count,
        user_connections=user_connections,
    )


# teacher dashboard route
@app.route("/teacher_dashboard")
@login_required
def teacher_dashboard():
    if current_user.user_type != "teacher":
        flash("Access denied. You are not a teacher.", "error")
        return redirect(url_for("home"))

    sort_announcements = sorted(
        announcements,
        key=lambda announcement: datetime.datetime.strptime(
            announcement["timestamp"], "%Y-%m-%d %H:%M:%S"
        ),
        reverse=True,
    )

    # Payment history
    all_payments = []
    for payment in announcement_payments:
        payment_user = users.get(str(payment.get("user_id")))
        payment_display = {
            "transaction_id": payment.get("transaction_id", "N/A"),
            "username": payment.get(
                "username", payment_user.username if payment_user else "Unknown"
            ),
            "user_id": payment.get("user_id", "N/A"),
            "title": payment.get("title", "Payment"),
            "amount": payment.get("amount", 0),
            "type": payment.get("type", "paid"),
            "card_info": payment.get("card_info", ""),
            "timestamp": payment.get("timestamp", ""),
        }
        all_payments.append(payment_display)

    # Sort by most recent first
    all_payments.sort(key=lambda p: p["timestamp"], reverse=True)

    user_notifications = get_user_notifications(current_user.id)
    unread_notification_count = get_unread_notification_count(current_user.id)

    # Connected accounts
    user_connections = get_connected_accounts(current_user.id)

    return render_template(
        "dashboard/teacher_dashboard.html",
        username=current_user.username,
        user_id=current_user.id,
        user_type=current_user.user_type,
        announcements=sort_announcements,
        all_payments=all_payments,
        notifications=user_notifications,
        unread_count=unread_notification_count,
        user_connections=user_connections,
    )


announcements_file = "announcements.json"
user_fees_file = "user_fees.json"
payment_history_file = "payments.json"


# Saves announcements to the file.
def save_announcements(announcements_data):
    with open(announcements_file, "w") as f:
        json.dump(announcements_data, f, indent=4)


# Loads announcements from the file.
def load_announcements():
    if os.path.exists(announcements_file):
        try:
            with open(announcements_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


# Saves user fees to the file.
def save_user_fees(fees_data):
    with open(user_fees_file, "w") as f:
        json.dump(fees_data, f, indent=4)


# Loads user fees from the file.
def load_user_fees():
    if os.path.exists(user_fees_file):
        try:
            with open(user_fees_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


# Saves payment history to the file.
def save_announcement_payments(payments_data):
    with open(payment_history_file, "w") as f:
        json.dump(payments_data, f, indent=4)


# Loads payment history from the file.
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

# Notifications
notifications_file = "notifications.json"


# Saves notifications to the file.
def save_notifications(notifications_data):
    with open(notifications_file, "w") as f:
        json.dump(notifications_data, f, indent=4)


# Loads notifications from the file.
def load_notifications():
    if os.path.exists(notifications_file):
        try:
            with open(notifications_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


notifications_list = load_notifications()

# Connected accounts
connected_accounts_file = "connected_accounts.json"


# Saves connected accounts to the file.
def save_connected_accounts(connections_data):
    with open(connected_accounts_file, "w") as f:
        json.dump(connections_data, f, indent=4)


# Loads connected accounts from the file.
def load_connected_accounts():
    if os.path.exists(connected_accounts_file):
        try:
            with open(connected_accounts_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


connected_accounts = load_connected_accounts()


# Finds a connection by its id.
def get_connection_by_id(connection_id):
    return next((c for c in connected_accounts if str(c.get("id")) == str(connection_id)), None)


# Finds the other user in a connection.
def get_other_user(connection, user_id):
    user_id_str = str(user_id)
    if str(connection.get("requester_id")) == user_id_str:
        return connection.get("user_id"), connection.get("recipient_name")
    return connection.get("requester_id"), connection.get("requester_name")


# Gets all connected accounts for a user.
def get_connected_accounts(user_id):
    user_id_str = str(user_id)
    connected = []
    for connection in connected_accounts:
        if connection.get("status") != "connected":
            continue
        if user_id_str not in (
            str(connection.get("requester_id")),
            str(connection.get("user_id")),
        ):
            continue
        other_id, other_name = get_other_user(connection, user_id_str)
        connected.append(
            {"connection_id": connection.get("id"), "user_id": other_id, "name": other_name}
        )
    return connected


# Gets the ids of connected users.
def get_connected_user_ids(user_id):
    return {str(a["user_id"]) for a in get_connected_accounts(user_id)}


# Sends the user to the right dashboard.
def get_user_dashboard_route():
    if current_user.user_type == "parent":
        return "parent_dashboard"
    elif current_user.user_type == "student":
        return "student_dashboard"
    elif current_user.user_type == "teacher":
        return "teacher_dashboard"
    return "home"


def redirect_to_dashboard():
    return redirect(url_for(get_user_dashboard_route()))


# Gets payment history for a user and their connections.
def get_combined_payment_history(user_id):
    ids = {str(user_id)} | get_connected_user_ids(user_id)
    history = []
    for save in announcement_payments:
        if str(save.get("user_id")) in ids:
            payment_type = save.get("type")
            if payment_type == "free":
                display_status = "Completed"
            elif payment_type == "refunded":
                display_status = "Refunded"
            else:
                display_status = "Paid"
            history.append(
                {
                    "description": save.get("title", "Announcement"),
                    "date": save.get("timestamp", ""),
                    "amount": save.get("amount", 0),
                    "status": display_status,
                    "paid_by": save.get("username", ""),
                }
            )
    history.sort(key=lambda p: p["date"], reverse=True)
    return history


# Creates notifications for an announcement.
def create_announcement_notifications(announcement, notification_type, exclude_user_id=None):
    target = announcement.get("target_users", "all")
    new_notifications = []

    for user_id, user in users.items():
        user_id_str = str(user_id)
        if exclude_user_id and str(exclude_user_id) == user_id_str:
            continue
        if target == "all":
            pass
        elif target == "students" and user.user_type != "student":
            continue
        elif target == "parents" and user.user_type != "parent":
            continue
        elif target == "teacher" and user.user_type != "teacher":
            continue

        title_prefix = "New Announcement" if notification_type == "published" else "Cancelled"
        title = f"{title_prefix}: {announcement['title']}"
        message = announcement["content"][:200] + (
            "..." if len(announcement["content"]) > 200 else ""
        )

        notification = {
            "id": str(random.randint(MIN_ID, MAX_ID)),
            "user_id": user_id_str,
            "announcement_id": announcement.get("id"),
            "type": notification_type,
            "title": title,
            "message": message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read": False,
        }
        new_notifications.append(notification)

    notifications_list.extend(new_notifications)
    save_notifications(notifications_list)
    return new_notifications


# Gets notifications for a user.
def get_user_notifications(user_id):
    user_id_str = str(user_id)
    user_notifications = [n for n in notifications_list if str(n.get("user_id")) == user_id_str]
    user_notifications.sort(key=lambda n: n.get("timestamp", ""), reverse=True)
    return user_notifications


@app.route("/mark_all_notifications_read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    for n in notifications_list:
        if str(n.get("user_id")) == str(current_user.id):
            n["read"] = True
    save_notifications(notifications_list)
    return {"success": True}


@app.route("/mark_notification_read/<notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    notification = next(
        (
            n
            for n in notifications_list
            if str(n.get("id")) == str(notification_id)
            and str(n.get("user_id")) == str(current_user.id)
        ),
        None,
    )

    if not notification:
        return jsonify({"success": False, "message": "Notification not found."}), 404

    notification["read"] = True
    save_notifications(notifications_list)
    return jsonify({"success": True})


# Connected accounts
@app.route("/connect_account", methods=["POST"])
@login_required
def connect_account():
    user_id = request.form.get("connect_user_id", "").strip()

    if not user_id:
        flash("Please enter a user ID.", "error")
        return redirect_to_dashboard()

    if user_id == str(current_user.id):
        flash("You cannot connect your account to itself.", "error")
        return redirect_to_dashboard()

    recipient = users.get(str(user_id))
    if not recipient:
        flash("No account was found with that user ID.", "error")
        return redirect_to_dashboard()

    requester_id = str(current_user.id)
    user_id = str(recipient.id)

    # Check for an existing connection between the two accounts
    existing = next(
        (
            c
            for c in connected_accounts
            if {str(c.get("requester_id")), str(c.get("user_id"))} == {requester_id, user_id}
            and c.get("status") == "connected"
        ),
        None,
    )
    if existing:
        flash(f"Your account is already connected to {recipient.username}.", "warning")
        return redirect_to_dashboard()

    connection = {
        "id": str(uuid.uuid4())[:12],
        "requester_id": requester_id,
        "requester_name": current_user.username,
        "user_id": user_id,
        "recipient_name": recipient.username,
        "status": "connected",
    }
    connected_accounts.append(connection)
    save_connected_accounts(connected_accounts)

    flash(f"Your account is now connected to {recipient.username}.", "success")
    return redirect_to_dashboard()


# Disconnect accounts
@app.route("/disconnect_connection/<connection_id>", methods=["POST"])
@login_required
def disconnect_connection(connection_id):
    connection = get_connection_by_id(connection_id)
    user_id_str = str(current_user.id)
    if not connection or user_id_str not in (
        str(connection.get("requester_id")),
        str(connection.get("user_id")),
    ):
        flash("Connection not found.", "error")
        return redirect_to_dashboard()

    connection["status"] = "disconnected"
    save_connected_accounts(connected_accounts)

    flash("Connection removed.", "success")
    return redirect_to_dashboard()


# Counts unread notifications for a user.
def get_unread_notification_count(user_id):
    user_id_str = str(user_id)
    return sum(
        1 for n in notifications_list if str(n.get("user_id")) == user_id_str and not n.get("read")
    )


# Gets fees for a user.
def get_user_fees(user_id):
    return user_fees.get(str(user_id), [])


# Adds a fee to a user.
def add_user_fee(user_id, fee_data):
    user_id_str = str(user_id)
    if user_id_str not in user_fees:
        user_fees[user_id_str] = []
    user_fees[user_id_str].append(fee_data)
    save_user_fees(user_fees)


# Marks a fee as paid.
def mark_user_fee_paid(user_id, fee_id):
    user_id_str = str(user_id)
    if user_id_str in user_fees:
        for fee in user_fees[user_id_str]:
            if str(fee.get("id")) == str(fee_id):
                fee["status"] = "Paid"
                break
        save_user_fees(user_fees)


# Route for making announcements (teacher only)
@app.route("/teacher/make_announcement", methods=["POST"])
@login_required
def make_announcement():
    if current_user.user_type != "teacher":
        return "Unauthorized: Only teachers can make announcements.", 403

    title = request.form.get("announcement_title")
    content = request.form.get("announcement_content")
    payment_select = request.form.get("payment_select")
    payment_amount = request.form.get("announcement_payment")
    target_users = request.form.get("target_users")

    if not all([title, content, payment_select, target_users]):
        flash("All fields are required!", "error")
        return redirect(url_for("teacher_dashboard"))

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
        "id": str(random.randint(MIN_ID, MAX_ID)),
        "title": title,
        "content": content,
        "payment_type": payment_type,
        "payment_amount": payment_amount_value,
        "target_users": target_users,
        "sender": current_user.username,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    announcements.append(new_announcement)
    save_announcements(announcements)

    # Send notification to target users
    create_announcement_notifications(
        new_announcement, "published", exclude_user_id=current_user.id
    )

    flash("Announcement published successfully!", "success")
    return redirect(url_for("teacher_dashboard"))


@app.route("/add_announcement_payment/<announcement_id>", methods=["POST"])
@login_required
def add_announcement_payment(announcement_id):
    if current_user.user_type not in ["parent", "teacher"]:
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
    fee_id = str(random.randint(MIN_ID, MAX_ID))
    new_fee = {
        "id": fee_id,
        "announcement_id": announcement_id,
        "name": announcement["title"],
        "amount": announcement.get("payment_amount", 0),
        "status": "Outstanding",
        "due_date": (datetime.date.today() + datetime.timedelta(days=FEE_DUE_DAYS)).strftime(
            "%m-%d-%Y"
        ),
        "added_on": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    add_user_fee(current_user.id, new_fee)
    flash(
        f"Announcement fee '{announcement['title']}' has been added to your payment fees.",
        "success",
    )
    return redirect(url_for("parent_dashboard"))


@app.route("/free_announcement_payment/<announcement_id>", methods=["POST"])
@login_required
def free_announcement_payment(announcement_id):
    if current_user.user_type not in ["parent", "teacher"]:
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
        if str(save.get("announcement_id")) == str(announcement_id) and str(
            save.get("user_id")
        ) == str(current_user.id):
            flash("You have already saved this free announcement.", "warning")
            return redirect(url_for("parent_dashboard"))

    # Save free announcements in history
    save = {
        "id": str(random.randint(MIN_ID, MAX_ID)),
        "announcement_id": announcement_id,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "title": announcement["title"],
        "type": "free",
        "amount": 0,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    announcement_payments.append(save)
    save_announcement_payments(announcement_payments)
    flash(f"Free announcement '{announcement['title']}' has been saved.", "success")
    return redirect(url_for("parent_dashboard"))


@app.route("/delete_user/<string:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    # Ensure only teachers can delete users
    if current_user.user_type != "teacher":
        return "Unauthorized: You must be a teacher to delete users.", 403
    
    user_id = str(user_id)

    # Prevent an teacher from deleting themselves
    if current_user.id == str(user_id) and current_user.user_type == "teacher":
        return "Error: You cannot delete your own account while logged in.", 404
    else:
        pass

    if str(user_id) in users:
        del users[str(user_id)]
        save_users(users)
        # Redirect back to the teacher dashboard
        return redirect(url_for("teacher_dashboard"))
    else:
        return "User not found.", 404


@app.route("/cancel_announcement/<string:announcement_id>", methods=["POST"])
@login_required
def cancel_announcement(announcement_id):
    if current_user.user_type != "teacher":
        return "Unauthorized", 403

    announcement = next((a for a in announcements if a["id"] == announcement_id), None)
    if not announcement:
        return "Announcement not found.", 404

    announcement["status"] = "cancelled"
    save_announcements(announcements)

    # Process refunds for users who already paid for this announcement
    # Find all paid fee IDs tied to this announcement (before removing fees)
    for user_id_str, fees in list(user_fees.items()):
        for fee in fees:
            if (
                str(fee.get("announcement_id")) == str(announcement_id)
                and fee.get("status") == "Paid"
            ):
                fee_id = fee.get("id")
                # Find the original payment record
                for payment in announcement_payments:
                    if str(payment.get("fee_id")) == str(fee_id) and payment.get("type") == "paid":
                        # Create a refund record in payment history
                        refund_record = {
                            "transaction_id": str(uuid.uuid4())[:12].upper(),
                            "id": payment.get("user_id"),
                            "user_id": payment.get("user_id"),
                            "username": payment.get("username"),
                            "title": f"Refund: {payment.get('title', 'Announcement')}",
                            "amount": payment.get("amount", 0),
                            "card_holder": payment.get("card_holder", ""),
                            "card_info": payment.get("card_info", ""),
                            "status": "Refunded",
                            "fee_id": payment.get("fee_id"),
                            "type": "refunded",
                            "announcement_id": announcement_id,
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        announcement_payments.append(refund_record)
                        break
    save_announcement_payments(announcement_payments)

    # Remove outstanding fees tied to this announcement
    for user_id_str, fees in list(user_fees.items()):
        user_fees[user_id_str] = [
            fee for fee in fees if str(fee.get("announcement_id")) != str(announcement_id)
        ]
        if not user_fees[user_id_str]:
            del user_fees[user_id_str]
    save_user_fees(user_fees)

    # Notify affected users
    create_announcement_notifications(announcement, "cancelled", exclude_user_id=current_user.id)

    flash(f"Announcement '{announcement['title']}' has been cancelled.", "success")
    return redirect(url_for("teacher_dashboard"))


# Get all user data (teacher only)
@app.route("/api/users")
@login_required
def get_users_api():
    # teacher users only
    if current_user.user_type != "teacher":
        return {"error": "Unauthorized access. Only teachers can view this information."}, 403

    users_data_for_api = {
        user_id: {
            "username": user_obj.username,
            "id": user_obj.id,
            "email": user_obj.email,
            "user_type": user_obj.user_type,
        }
        for user_id, user_obj in users.items()
    }
    return users_data_for_api, 200


@app.route("/profile/<string:user_id>")
@login_required
def user_profile(user_id):
    user_id = user_id.replace(" ", "_")
    user = users.get(str(user_id))
    if not user:
        return "User not found", 404

    # Payment history per-user (visible to teachers)
    payment_history = []
    if current_user.user_type == "teacher":
        user_id_str = str(user.id)
        for save in announcement_payments:
            if str(save.get("user_id")) == user_id_str:
                payment_type = save.get("type")
                if payment_type == "free":
                    display_status = "Completed"
                elif payment_type == "refunded":
                    display_status = "Refunded"
                else:
                    display_status = "Paid"
                payment_history.append(
                    {
                        "transaction_id": save.get("transaction_id", "N/A"),
                        "description": save.get("title", "Payment"),
                        "date": save.get("timestamp", ""),
                        "amount": save.get("amount", 0),
                        "type": save.get("type", "paid"),
                        "card_info": save.get("card_info", ""),
                        "status": display_status,
                    }
                )
        # Sort most recent first
        payment_history.sort(key=lambda p: p["date"], reverse=True)

    # Connected accounts for this user (visible to teachers)
    user_connections = []
    if current_user.user_type == "teacher":
        user_connections = get_connected_accounts(user.id)

    return render_template(
        "profile.html",
        user=user,
        user_id=user_id,
        payment_history=payment_history,
        user_connections=user_connections,
    )


# About page route
@app.route("/about")
def about():
    return render_template("about.html")


# Contact page route
@app.route("/contact")
def contact():
    return render_template("contact.html")


# Payment route
@app.route("/payment", defaults={"fee_id": None})
@app.route("/payment/<fee_id>")
@login_required
def payment(fee_id):
    prefill_data = {}
    if fee_id:
        user_fees_list = get_user_fees(current_user.id)

        selected_fee = next(
            (
                fee
                for fee in user_fees_list
                if str(fee.get("id")) == str(fee_id) and fee.get("status") == "Outstanding"
            ),
            None,
        )

        if selected_fee:
            prefill_data = {
                "amount": selected_fee.get("amount", 0),
                "fee_name": selected_fee.get("name", "Payment"),
                "fee_id": fee_id,
            }

    current_year = datetime.datetime.now().year
    return render_template(
        "payment.html",
        prefill_data=prefill_data,
        dashboard_route=get_user_dashboard_route(),
        current_year=current_year,
    )


@app.route("/make_payment", methods=["POST"])
@login_required
def make_payment():
    try:
        student_id = request.form.get("student_id")
        amount_str = request.form.get("amount")
        card_name = request.form.get("card_holder_name")
        card_number = (request.form.get("card_number") or "").strip()
        exp_month = request.form.get("exp_month")
        exp_year = request.form.get("exp_year")
        fee_id = request.form.get("fee_id")
        fee_name = request.form.get("fee_name", "Payment")
        transaction_id = str(uuid.uuid4())[:12].upper()
        current_year = datetime.datetime.now().year

        # Validate amount (handles missing or non number values)
        try:
            amount = float(amount_str)
        except (TypeError, ValueError):
            prefill_data = {
                "amount": amount_str,
                "card_holder_name": card_name,
                "fee_id": fee_id,
                "fee_name": fee_name,
            }
            return render_template(
                "payment.html",
                error="Invalid payment amount.",
                prefill_data=prefill_data,
                dashboard_route=get_user_dashboard_route(),
                current_year=current_year,
            )

        # Reject negative or unreasonably large amounts
        if amount <= 0 or amount > 1000000:
            prefill_data = {
                "amount": amount_str,
                "card_holder_name": card_name,
                "fee_id": fee_id,
                "fee_name": fee_name,
            }
            return render_template(
                "payment.html",
                error="Payment amount must be greater than $0.00.",
                prefill_data=prefill_data,
                dashboard_route=get_user_dashboard_route(),
                current_year=current_year,
            )

        # Validate card number length before slicing
        if not card_number or len(card_number) < 4 or not card_number.isdigit():
            prefill_data = {
                "amount": amount_str,
                "card_holder_name": card_name,
                "fee_id": fee_id,
                "fee_name": fee_name,
            }
            return render_template(
                "payment.html",
                error="Invalid card number.",
                prefill_data=prefill_data,
                dashboard_route=get_user_dashboard_route(),
                current_year=current_year,
            )

        # Validate expiry date
        try:
            exp_month_int = int(exp_month)
            exp_year_int = int(exp_year)
            if not (1 <= exp_month_int <= 12):
                raise ValueError("Invalid month")
        except (TypeError, ValueError):
            prefill_data = {
                "amount": amount_str,
                "card_holder_name": card_name,
                "fee_id": fee_id,
                "fee_name": fee_name,
            }
            return render_template(
                "payment.html",
                error="Invalid card expiry date.",
                prefill_data=prefill_data,
                dashboard_route=get_user_dashboard_route(),
                current_year=current_year,
            )

        now = datetime.datetime.now()
        if (exp_year_int, exp_month_int) < (now.year, now.month):
            prefill_data = {
                "amount": amount_str,
                "card_holder_name": card_name,
                "fee_id": fee_id,
                "fee_name": fee_name,
            }
            return render_template(
                "payment.html",
                error="Card has expired. Please use a valid card.",
                prefill_data=prefill_data,
                dashboard_route=get_user_dashboard_route(),
                current_year=current_year,
            )

        card_preview = f"Card Ending in {card_number[-4:]}"

        payment_record = {
            "transaction_id": transaction_id,
            "student_id": student_id,
            "user_id": str(current_user.id),
            "username": current_user.username,
            "title": fee_name,
            "amount": amount,
            "card_holder": card_name,
            "card_info": card_preview,
            "status": "Paid",
            "fee_id": fee_id,
            "type": "paid",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Mark the fee as paid
        if fee_id:
            mark_user_fee_paid(current_user.id, fee_id)

        teacher_dashboard_data.append(payment_record)
        announcement_payments.append(payment_record)
        save_announcement_payments(announcement_payments)

        return render_template(
            "make_payment.html",
            student_id=student_id,
            amount=amount,
            card_holder=card_name,
            card_info=card_preview,
            status="Paid",
            timestamp=payment_record["timestamp"],
            transaction_id=transaction_id,
            fee_name=fee_name,
            dashboard_route=get_user_dashboard_route(),
        )

    except Exception:
        return render_template(
            "payment.html",
            error="Payment failed. Please try again.",
            prefill_data={},
            dashboard_route=get_user_dashboard_route(),
            current_year=datetime.datetime.now().year,
        )


if __name__ == "__main__":
    app.run(debug=True, port=8001)
