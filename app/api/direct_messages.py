from flask import Blueprint, request, flash, redirect, url_for
from flask_socketio import send, emit
from flask_login import login_user,login_required, current_user, logout_user
# local
from app import db
from app.extensions import socketio
from app.models import User, Companies, Jobs,DirectMessages,Notifications
from datetime import datetime

from app.utils.validate_data import is_form_empty



direct_messages_bp = Blueprint("direct_messages",__name__)


# here will create the api to crud msg 

@socketio.on('connect')
def handle_message(data):
    print('received message: ' + data)


# @direct_messages_bp.route("message/new",  methods=["POST"])
# @login_required
# def send_new_message():
#     try:
#         # Debug logging
#         print("Form data:", request.form)
#         if is_form_empty(request.form):
#             flash("No data provided in the form.", "warning")
#             redirect(request.referrer or url_for('frontend.messages'))



#     except Exception as e:
#         db.session.rollback()
#         print("Error sending message:", str(e))
#         flash("Error sending message", "danger")

#     return redirect(request.referrer or url_for('frontend.messages'))