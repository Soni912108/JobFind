from flask import Blueprint, render_template, request, redirect, jsonify,url_for, flash
from flask import session
from flask_login import login_user,login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import (User, Companies, Jobs, DirectMessages, Notifications,Applications)
from app import db
from app.utils.validate_data import (validate_register_data, validate_login_data,is_form_empty,
                                     validate_register_company_data,validate_register_user_data)

from sqlalchemy import or_


frontend_bp = Blueprint("frontend",__name__)

# Home
@frontend_bp.route("/")
def index():
    return render_template("index.html")

# Jobs - feed
@frontend_bp.route("/jobs")
@login_required
def jobs():
    requested_page = request.args.get('page', 1, type=int)
    page = max(1, requested_page)
    per_page = 12

    search_for = request.args.get('search', '').strip()
    if search_for:
        base_query = Jobs.query.filter(Jobs.title.ilike(f"%{search_for}%"))
    else:
        base_query = Jobs.query

    jobs_pagination = base_query.order_by(Jobs.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    jobs_list = jobs_pagination.items

    print("=== Jobs Debug ===")
    for job in jobs_list:
        if isinstance(current_user, Companies):
            job.is_owner = job.company_id == current_user.id
            print(f"Job {job.id} - Owner: {job.is_owner}")
        else:
            application = Applications.query.filter_by(job_id=job.id, user_id=current_user.id).first()
            job.already_applied = application is not None
            print(f"Job {job.id} - Applied: {job.already_applied}")
        
        job.number_of_applicants = Applications.query.filter_by(job_id=job.id).count()
        print(f"Number of applicants {job.number_of_applicants}")
    print("=== Jobs Debug ===")
    return render_template(
        "jobs/jobs.html",
        active="jobs", 
        pagination=jobs_pagination,
        jobs=jobs_list,
        total_count=jobs_pagination.total,
        user=current_user
    )



# view_applications.html
@frontend_bp.route("/applications", methods=["GET"])
@login_required
def applications_page():
    # Check if current user is not a user - only users ca view the application page
    if not isinstance(current_user, User):
        flash("Can open this page!", "info")
        return redirect(request.referrer or url_for('frontend.jobs'))
    
    # Get and sanitize parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_term = request.args.get('search', '').strip()
    
    # Debug logging
    print("=== Applications Search Debug ===")
    print(f"User ID: {current_user.id}")
    print(f"Search term: '{search_term}'")
    print(f"Page: {page}, Per_page: {per_page}")
    
    # Base query
    base_query = db.session.query(
        Jobs,
        Applications
    ).join(
        Applications,
        Jobs.id == Applications.job_id
    ).filter(
        Applications.user_id == current_user.id
    )
    # check the len of the base_query, if 0 than user has not applied to any jobs
    applications_count = base_query.count()
    print(f"Applications found: {applications_count}")
    if applications_count == 0:
        flash("You haven't applied to any jobs yet!", "info")
        return render_template("applications/view_applications.html", applications=[],user=current_user)
    # Add search filter if provided
    if search_term:
        base_query = base_query.filter(Jobs.title.ilike(f"%{search_term}%"))
    
    # Add ordering
    query = base_query.order_by(Applications.applied_at.desc())
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Debug results
    print("\nQuery Results:")
    for job, application in pagination.items:
        print(f"Found Job: {job.title} (ID: {job.id}), Applied: {application.applied_at}(ID: {application.id})")
        
    print(f"Total results: {pagination.total}\n")
    
    return render_template(
        "applications/view_applications.html",
        applications=pagination.items,
        pagination=pagination,
        total_count=pagination.total,
        user=current_user,
    )


# Notifications
@frontend_bp.route("/notifications")
@login_required
def notifications():
    requested_page = request.args.get('page', 1, type=int)
    page = max(1, requested_page)
    per_page = 12

    search_for = request.args.get('search', '').strip()
    if search_for:
        base_query = Notifications.query.filter(Notifications.title.ilike(f"%{search_for}%"))
    else:
        base_query = Notifications.query

    # Get paginated jobs
    notifications_pagination = base_query.order_by(Notifications.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    msg_list = notifications_pagination.items

    return render_template(
        "notifications/notifications.html",
        active="notifications", 
        pagination=notifications_pagination,
        notifications=msg_list,
        total_count=notifications_pagination.total,
        user=current_user
    )

# Messages
@frontend_bp.route("/messages")
@login_required
def messages():
    requested_page = request.args.get('page', 1, type=int)
    page = max(1, requested_page)
    per_page = 12

    search_for = request.args.get('search', '').strip()
    if search_for:
        # filter only the messages that were send or received by the current_user.id
        base_query = DirectMessages.query.filter((DirectMessages.sender_id == current_user.id) | (DirectMessages.receiver_id == current_user.id),
                                                DirectMessages.title.ilike(f"%{search_for}%"))
    else:
        base_query = DirectMessages.query.filter((DirectMessages.sender_id == current_user.id) | (DirectMessages.receiver_id == current_user.id))

    # Get paginated jobs
    msg_pagination = base_query.order_by(DirectMessages.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    msg_list = msg_pagination.items

    return render_template(
        "dms/messages.html",
        active="messages", 
        pagination=msg_pagination,
        messages=msg_list,
        total_count=msg_pagination.total,
        user=current_user
    )


# Authentication
@frontend_bp.route("/users/login")
def login():
    return render_template("users/login.html", active="login")


@frontend_bp.route("/users/login", methods=["POST"])
def login_post():
    req_data = request.form
    print(f"Login data: {req_data}")
    
    if is_form_empty(req_data):
        flash("No data provided in the form.", "warning")
        return redirect(url_for("frontend.login"))
    
    errors = validate_login_data(req_data)
    if errors:
        for error in errors:
            flash(error, "warning")
        return redirect(url_for("frontend.login"))

    user_type = req_data.get("user_type")
    email=req_data.get("email")
    user = None

    if user_type == "Person":
        user = User.query.filter_by(email=email).first()
    elif user_type == "Company":
        user = Companies.query.filter_by(email=email).first()

    if not user:
        flash(f"{user_type} not found.", "danger")
        return redirect(url_for("frontend.login"))

    # Check password
    if check_password_hash(user.password, req_data.get("password")):
        # Store user type in the session
        session["user_type"] = user_type
        login_user(user, remember=req_data.get("remember", False))
        flash("Login successful!", "success")
        return redirect(url_for("frontend.jobs"))
    else:
        flash("Invalid credentials.", "danger")
        return redirect(url_for("frontend.login"))



@frontend_bp.route("/users/register")
def register():
    return render_template("users/register.html", active="register")

@frontend_bp.route('/register', methods=['POST'])
def register_post():
    try:
        req_data = request.form
        print(f"Register data: {req_data}")
        # Check if the form is empty
        if is_form_empty(req_data):
            flash("No data provided in the form.", "warning")
            return redirect(url_for("frontend.register"))
        # Validate the data provided, this is for common fields of both company and person
        errors = validate_register_data(req_data)
        if errors:
            for error in errors:
                flash(error, "warning")
            return redirect(url_for("frontend.register"))
        # Here we have passed the common fields validation, now we can check for user_type(is certain its either Person or Company)
        if req_data.get("user_type") == 'Person':
            errors = validate_register_user_data(req_data)
            if errors:
                for error in errors:
                    flash(error, "warning")
                return redirect(url_for("frontend.register"))
            # # Check email exists in User table - check moved to validate_register_user_data
            # if User.query.filter_by(email=req_data.get("email")).first():
            #     flash("Email already registered as Person.", "warning")
            #     return redirect(url_for("frontend.register"))
            
            # Create User
            user = User(
                email=req_data.get("email"),
                name=req_data.get("name"),
                surname=req_data.get("surname"),
                profession=req_data.get("profession"),
                password=generate_password_hash(req_data.get("password"),method='pbkdf2')
            )
            db.session.add(user)
            
        elif req_data.get("user_type") == 'Company':
            # Validate Company fields
            errors = validate_register_company_data(req_data)
            if errors:
                for error in errors:
                    flash(error, "warning")
                return redirect(url_for("frontend.register"))
            # Check email exists in Companies table - check moved to validate_register_company_data
            # if Companies.query.filter_by(email=req_data.get("email")).first():
            #     flash("Email already registered as Company.", "warning")
            #     return redirect(url_for("frontend.register"))
            
            # Create Company
            company = Companies(
                email=req_data.get("email"),
                name=req_data.get("name"),
                description=req_data.get("description"),
                location=req_data.get("location"),
                password=generate_password_hash(req_data.get("password"))
            )
            db.session.add(company)

        db.session.commit()
        flash("Registration successful", "success")
        return redirect(url_for('frontend.login'))

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        flash('Error during registration', "danger")
        return redirect(url_for('frontend.register'))



# Logout 
@frontend_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()  # Clears the session
    flash("You have been logged out.", "info")
    return redirect(url_for("frontend.login"))