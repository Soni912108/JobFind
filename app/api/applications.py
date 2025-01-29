from flask import Blueprint, request, render_template,flash, redirect, url_for,jsonify,session
from app import db
from app.models import User, Companies, Jobs, applications
from datetime import datetime
from flask_login import login_required, current_user
from app.helpers.validate_data import is_form_empty

applications_bp = Blueprint("applications",__name__)

# view_applications.html
@applications_bp.route("/all", methods=["GET"])
@login_required
def applications_page():
    try:
        # Check if current user is not a user - only users ca view the application page
        if not isinstance(current_user, User):
            flash("Can open this page!", "info")
            return redirect(request.referrer or url_for('frontend.jobs'))
        # ADD PAGINATION AND SEARCH HERE
        # Query applications for current user
        user_applications = db.session.query(
            Jobs,
            applications.c.applied_at
        ).join(
            applications,
            Jobs.id == applications.c.job_id
        ).filter(
            applications.c.user_id == current_user.id
        ).order_by(
            applications.c.applied_at.desc()
        ).all()

        print("=== Debug: User Applications ===")
        for job, applied_at in user_applications:
            print(f"Job ID: {job.id}")
            print(f"Job Title: {job.title}")
            print(f"Company ID: {job.company_id}")
            print(f"Applied At: {applied_at}")
            print("----------------------------")
        print(f"Total Applications: {len(user_applications)}")
        
        return render_template(
            "applications/view_applications.html",
            applications=user_applications,
            active='applications',
            user=current_user
        )
    except Exception as e:
        print("Error fetching applications:", str(e))
        flash("Error loading applications", "danger")
        return render_template(
            "applications/view_applications.html",
            user=current_user,
            applications=[])