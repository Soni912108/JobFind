from flask import Blueprint, request, flash, redirect, url_for,jsonify,session
from flask_login import login_required, current_user
# local
from app import db
from app.models import User, Companies, Jobs, Applications
from datetime import datetime
from .notifications import create_notification
from app.utils.validate_data import is_form_empty

jobs_bp = Blueprint("jobs",__name__)

# Create a new job
@jobs_bp.route("/job/create", methods=["POST"])
@login_required
def create_job():
    try:
        # Debug logging
        print("Form data:", request.form)
        if is_form_empty(request.form):
            flash("No data provided in the form.", "warning")
            redirect(request.referrer or url_for('frontend.jobs'))
        
        # Check if current user is a company
        if not isinstance(current_user, Companies):
            flash("Only companies can create a job", "danger")
            return redirect(request.referrer or url_for('frontend.jobs'))
        
        # Verify company exists
        company = Companies.query.filter_by(email=current_user.email).first()
        if not company:
            flash("Company not found", "danger")
            return redirect(request.referrer or url_for('frontend.jobs'))
        print(f"Description Length: {len(request.form.get('description'))}")
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
@jobs_bp.route("/job/info/<int:job_id>", methods=["GET"])
@login_required
def job_detail(job_id):
    job = Jobs.query.filter_by(id=job_id).first()
    if not job:
        return jsonify({"error": "Job not found"})

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
@jobs_bp.route("/job/update/", methods=["POST"])
@login_required
def update_job():
    job_id = request.form.get('editJobId')
    if not job_id:
        flash("An unexpected error occurred", "warning")
        return redirect(url_for('frontend.index'))
    # make sure job exists and belongs to the current user
    job = Jobs.query.filter_by(company_id=current_user.id, id=job_id).first()
    if not job:
        flash("Can not update this job - either not under this company or does not exists", "danger")
        return redirect(request.referrer or url_for('frontend.jobs'))

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

    return redirect(request.referrer or url_for('frontend.jobs'))


# delete job
@jobs_bp.route("/job/delete/", methods=["POST"])
@login_required
def delete_job():
    print("Delete job form data:", request.form)
    job_id = request.form.get("jobId")
    if not job_id:
        flash("An unexpected error occurred", "warning")
        return redirect(url_for('frontend.index'))
    # make sure job exists and belongs to the current user
    job = Jobs.query.filter_by(company_id=current_user.id, id=job_id).first()
    print(f"Job to delete: ID={job.id}, Title={job.title}, Description={job.description}, Location={job.location}")
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

    return redirect(request.referrer or url_for('frontend.jobs'))



# Apply for a job
@jobs_bp.route("/job/apply/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):

    print("==== Job Application Debug ====")
    print(f"Request Method: {request.method}")
    print(f"Job ID from URL: {job_id}")

    # Check if job exists
    job = Jobs.query.filter_by(id=job_id).first()
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    # check if the user is a Company
    if isinstance(current_user, Companies) or session.get('user_type') == 'Company':
        return jsonify({"error": "Only Professionals can apply for jobs."}),409
    # Base query
    already_applied = Applications.query.filter_by(job_id=job.id, user_id=current_user.id).first()
    print(already_applied)
    print("============================")
    # Check if already applied  
    if already_applied is not None:
        return jsonify({"error": "You have already applied for this job"}), 409

    try:
        # Add application with timestamp
        application = Applications(
            user_id=current_user.id,
            job_id=job_id,
            company_id=job.company_id,
            applied_at=datetime.now()
        )
        db.session.add(application)
        db.session.commit()

        # Create a notification for the company receiving the application.
        notif_message = f"{current_user.name} applied for your job '{job.title}'"
        create_notification(job.company_id, notif_message, emit_notification=True)

        return jsonify({"message": "Application submitted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print("Error applying for job:", str(e))
        return jsonify({"error": "Error applying for job"}), 500

    