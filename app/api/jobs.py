from flask import Blueprint, request, flash, redirect, url_for,jsonify
from app import db
from app.models import User, Companies, Jobs
from datetime import datetime
from flask_login import login_user,login_required, current_user, logout_user
from app.helpers.validate_data import is_form_empty

jobs_bp = Blueprint("jobs",__name__)

# Create a new job
@jobs_bp.route("/jobs/create", methods=["POST"])
@login_required
def create_job():
    try:
        # Debug logging
        print("Form data:", request.form)
        if is_form_empty(request.form):
            flash("No data provided in the form.", "warning")
            redirect(request.referrer or url_for('frontend.jobs'))
        
        # Verify company exists
        company = Companies.query.filter_by(email=current_user.email).first()
        if not company:
            flash("Company not found", "danger")
            return redirect(request.referrer or url_for('frontend.jobs'))
        # Check if current user is a company
        if not isinstance(current_user, Companies):
            flash("Only companies can create a job", "danger")
            return redirect(request.referrer or url_for('frontend.jobs'))

        # Create new job with verified company_id
        new_job = Jobs(
            title=request.form.get('jobtitle'),
            description=request.form.get('description'),
            location=request.form.get('joblocation'),
            salary=request.form.get('jobsalary'),
            company_id=company.id  # Use verified company id
        )

        # Add and commit to database
        db.session.add(new_job)
        db.session.commit()

        flash("Job created successfully", "success")


    except Exception as e:
        db.session.rollback()
        print("Error creating job:", str(e))
        flash("Error creating job", "danger")

    return redirect(request.referrer or url_for('frontend.jobs'))

# job detail
@jobs_bp.route("/jobs/info/<int:job_id>", methods=["POST"])
@login_required
def job_detail(job_id):
    job = Jobs.query.filter_by(company_id=current_user.id, id=job_id).first()
    if not job:
        flash("Job not found", "danger")
        return redirect(url_for('frontend.jobs'))

    return jsonify({
        "job_id": job.id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "salary": job.salary,
        "company_id": job.company_id,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    })


# Update job
@jobs_bp.route("/jobs/update/", methods=["POST"])
@login_required
def update_job():
    job_id = request.form.get('editJobId')
    # make sure job exists and belongs to the current user
    job = Jobs.query.filter_by(company_id=current_user.id, id=job_id).first()
    if not job:
        flash("Can not update this job - either not under this company or does not exists", "danger")
        return redirect(url_for('frontend.jobs'))

    try:
        job.title = request.form.get('editJobTitle')
        job.description = request.form.get('editJobDescription')
        job.location = request.form.get('editJobLocation')
        job.salary = request.form.get('editJobSalary')
        job.updated_at = datetime.now()

        db.session.commit()
        flash("Job updated successfully", "success")
    except Exception as e:
        db.session.rollback()
        print("Error updating job:", str(e))
        flash("Error updating job", "danger")

    return redirect(url_for('frontend.jobs'))


# delete job
@jobs_bp.route("/jobs/delete/", methods=["POST"])
@login_required
def delete_job(job_id):
    # make sure job exists and belongs to the current user
    job = Jobs.query.filter_by(company_id=current_user.id, id=job_id).first()
    if not job:
        flash("Can not delete this job - either not under this company or does not exists", "danger")
        return redirect(url_for('frontend.jobs'))

    try:
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        print("Error deleting job:", str(e))
        flash("Error deleting job", "danger")

    return redirect(url_for('frontend.jobs'))
