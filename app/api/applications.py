from flask import Blueprint, request, render_template,flash, redirect, url_for,jsonify,session
from app import db
from app.models import User, Companies, Jobs,Applications
from datetime import datetime
from flask_login import login_required, current_user
from app.helpers.validate_data import is_form_empty

applications_bp = Blueprint("applications",__name__)

# here will create the api to crud applications


@applications_bp.route("/application/delete/", methods=["POST"])
@login_required
def delete_application():
    print(f"Delete application request form {request.form}")
    application_id = request.form.get('applicationId')
    if not application_id:
        flash("An unexpected error occurred", "warning")
        return redirect(url_for('frontend.index'))
    
    # find the application and delete it
    find_application = Applications.query.filter_by(id=application_id,user_id=current_user.id).first()
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



applications_bp.route("/application/kot/", methods=["POST"])
@login_required
def kot():
    return