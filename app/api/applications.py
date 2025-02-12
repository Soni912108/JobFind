from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, session
from app import db
from app.models import User, Person, Company, Job, JobApplication
from datetime import datetime
from flask_login import login_required, current_user
from app.utils.validate_data import is_form_empty

applications_bp = Blueprint("applications", __name__)

# here will create the api to crud applications

@applications_bp.route("/application/delete/", methods=["POST"])
@login_required
def delete_application():
    print(f"Delete application request form {request.form}")
    application_id = request.form.get('applicationId')
    if not application_id:
        flash("An unexpected error occurred", "warning")
        return redirect(url_for('frontend.index'))
    
    # find the application and delete it - now using the unified User model
    find_application = JobApplication.query.filter_by(
        id=application_id,
        applicant_id=current_user.id
    ).first()
    
    print(find_application)
    if not find_application:
        flash("Application not found", "warning")
        return redirect(url_for('frontend.applications_page'))

    try:
        db.session.delete(find_application)
        db.session.commit()
        flash("Application deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        print("Error deleting application:", str(e))
        flash("Error deleting application", "danger")

    return redirect(url_for('frontend.applications_page'))

@applications_bp.route("/application/update/", methods=["POST"])
@login_required
def update_application():
    # Check if user is a Person
    if not isinstance(current_user, Person) or not current_user.can_apply_to_job():
        flash("Only Professionals can update applications", "danger")
        return redirect(url_for('frontend.applications_page'))

    application_id = request.form.get('applicationId')
    if not application_id:
        flash("An unexpected error occurred", "warning")
        return redirect(url_for('frontend.index'))

    # Find application using the unified User model
    application = JobApplication.query.filter_by(
        id=application_id,
        applicant_id=current_user.id
    ).first()

    if not application:
        flash("Application not found", "warning")
        return redirect(url_for('frontend.applications_page'))

    try:
        # Update application fields
        if 'resume' in request.form:
            application.resume = request.form.get('resume')
        
        application.updated_at = datetime.now()
        db.session.commit()
        flash("Application updated successfully", "success")
    except Exception as e:
        db.session.rollback()
        print("Error updating application:", str(e))
        flash("Error updating application", "danger")

    return redirect(url_for('frontend.applications_page'))

@applications_bp.route("/application/list/<int:job_id>", methods=["GET"])
@login_required
def list_applications(job_id):
    # Check if user is a Company and owns the job
    if not isinstance(current_user, Company):
        return jsonify({"error": "Unauthorized access"}), 403

    job = Job.query.filter_by(id=job_id, company_id=current_user.id).first()
    if not job:
        return jsonify({"error": "Job not found or unauthorized"}), 404

    try:
        # Get all applications for this job with applicant details
        applications = JobApplication.query\
            .filter_by(job_id=job_id)\
            .join(Person, JobApplication.applicant_id == Person.id)\
            .all()

        applications_list = []
        for app in applications:
            applications_list.append({
                "id": app.id,
                "applicant_name": app.applicant.name,
                "applicant_email": app.applicant.email,
                "resume": app.resume if hasattr(app, 'resume') else None,
                "applied_at": app.applied_at.strftime("%Y-%m-%d %H:%M:%S") if app.applied_at else None,
                "updated_at": app.updated_at.strftime("%Y-%m-%d %H:%M:%S") if app.updated_at else None
            })

        return jsonify({
            "applications": applications_list,
            "total": len(applications_list)
        })

    except Exception as e:
        print("Error fetching applications:", str(e))
        return jsonify({"error": "Error fetching applications"}), 500

@applications_bp.route("/application/detail/<int:application_id>", methods=["GET"])
@login_required
def application_detail(application_id):
    try:
        # For Person: get their own application
        # For Company: get application for their job
        if isinstance(current_user, Person):
            application = JobApplication.query\
                .filter_by(id=application_id, applicant_id=current_user.id)\
                .first()
        elif isinstance(current_user, Company):
            application = JobApplication.query\
                .join(Job)\
                .filter(
                    JobApplication.id == application_id,
                    Job.company_id == current_user.id
                ).first()
        else:
            return jsonify({"error": "Unauthorized access"}), 403

        if not application:
            return jsonify({"error": "Application not found or unauthorized"}), 404

        return jsonify({
            "id": application.id,
            "job_title": application.job.title,
            "company_name": application.job.company.name,
            "applicant_name": application.applicant.name,
            "applicant_email": application.applicant.email,
            "resume": application.resume if hasattr(application, 'resume') else None,
            "applied_at": application.applied_at.strftime("%Y-%m-%d %H:%M:%S") if application.applied_at else None,
            "updated_at": application.updated_at.strftime("%Y-%m-%d %H:%M:%S") if application.updated_at else None
        })

    except Exception as e:
        print("Error fetching application details:", str(e))
        return jsonify({"error": "Error fetching application details"}), 500

