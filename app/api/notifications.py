from flask import Blueprint, request, flash, redirect, url_for
from app import db
from app.models import User, Companies, Jobs
from datetime import datetime
from flask_login import login_user,login_required, current_user, logout_user

notifications_bp = Blueprint("notifications",__name__)

@notifications_bp.route("/application/delete/", methods=["POST"])
@login_required
def delete_application():
    # Base query
    # base_query = db.session.query(
    #     Jobs,
    #     applications.c.applied_at
    # ).join(
    #     applications,
    #     Jobs.id == applications.c.job_id
    # ).filter(
    #     applications.c.user_id == current_user.id
    # )
    pass