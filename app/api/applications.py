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
        applications.c.applied_at
    ).join(
        applications,
        Jobs.id == applications.c.job_id
    ).filter(
        applications.c.user_id == current_user.id
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
    query = base_query.order_by(applications.c.applied_at.desc())
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Debug results
    print("\nQuery Results:")
    for job, applied_at in pagination.items:
        print(f"Found Job: {job.title} (ID: {job.id}), Applied: {applied_at}")
    print(f"Total results: {pagination.total}\n")
    
    return render_template(
        "applications/view_applications.html",
        applications=pagination.items,
        pagination=pagination,
        total_count=pagination.total,
        user=current_user,
    )
