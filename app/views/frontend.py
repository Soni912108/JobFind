from flask import Blueprint, render_template, request, redirect, jsonify,url_for, flash
from flask_login import login_user,login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import (User, Companies, Jobs, DirectMessages, Notifications)
from app import db

frontend_bp = Blueprint("frontend",__name__)

# Home
@frontend_bp.route("/")
@login_required
def index():
    return render_template("base.html", active="dashboard", user=current_user)

# Jobs - feed
@frontend_bp.route("/jobs")
@login_required
def jobs():
    all_jobs = Jobs.query.all()
    return render_template("jobs/jobs.html", active="jobs", jobs=all_jobs)

# Notifications
@frontend_bp.route("/notifications")
@login_required
def notifications():
    all_notifications = Notifications.query.all(receiver_id=current_user.id)
    return render_template(
        "notifications/all_notifications.html", 
        active="notifications",
        all_notifications=all_notifications
        )

# Messages
@frontend_bp.route("/messages")
@login_required
def messages():
    all_messages = DirectMessages.query.filter_by(receiver_id=current_user.id).all()
    return render_template("dms/messages.html", active="messages", all_messages=all_messages)



# Authentication for users(Person)
@frontend_bp.route("/users/login")
def users_login():
    return render_template("users/login.html", active="login")

@frontend_bp.route("/users/login",methods=["POST"])
def users_login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return redirect(url_for("frontend.index"))
    else:
        flash("Invalid Credentials.", "danger")
        return redirect(url_for("frontend.users_login"))


@frontend_bp.route("/users/register")
def users_register_get():
    return render_template("users/register.html")

@frontend_bp.route('/users/register', methods=['POST'])
def users_register_post():
    try:
        # Get form data
        email = request.form.get('email')
        name = request.form.get('name')
        surname = request.form.get('surname')
        profession = request.form.get('profession')
        password = request.form.get('password')
        # Validate required fields
        if not all([email, password, name, surname, profession]):
            return jsonify({'error': 'All fields are required'}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create new user
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            name=name,
            surname=surname,
            profession=profession
        )

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("frontend.users_login"))

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# Authentication for Companies(Company)
@frontend_bp.route("/company/login")
def company_login():
    return render_template("company/login.html", active="login")

@frontend_bp.route("/company/login",methods=["POST"])
def company_login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = Companies.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return redirect(url_for("frontend.index"))
    else:
        flash("Invalid Credentials.", "danger")
        return redirect(url_for("frontend.company_login"))


@frontend_bp.route("/company/register")
def company_register_get():
    return render_template("company/register.html")

@frontend_bp.route("/company/register", methods=["POST"])
def company_register_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    user = Companies.query.filter_by(email=email).first()

    if user:
        flash("Email address already exists")
        return redirect(url_for("frontend.company_register_get"))

    new_user = Companies(email=email, name=name, password=generate_password_hash(password,method="pbkdf2"))
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("frontend.company_login"))



# Should change this to post - check if Person or Company before redirecting to login/
@frontend_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("frontend.users_login"))