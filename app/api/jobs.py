from flask import Blueprint, request, flash, redirect, url_for
from app import db
from app.models import User, Companies, Jobs
from datetime import datetime
from flask_login import login_user,login_required, current_user, logout_user


jobs_bp = Blueprint("jobs",__name__)

# Create a new job
@jobs_bp.route("/jobs/create", methods=["POST"])
@login_required
def create_job():
    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("location")
    salary = request.form.get("salary")
    
    new_job = Jobs(
        title=title, 
        description=description,
        location=location,
        salary=salary, 
        company_id=current_user.company_id
    )
    # Add new campaign to db
    try:
        db.session.add(new_job)
        db.session.commit()
        flash("Job added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while creating the job.", "danger")
        print(f"Error: {e}")  # for debug purposes

    return redirect(url_for("frontend.jobs"))