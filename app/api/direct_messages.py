from flask import Blueprint, request, flash, redirect, url_for,jsonify
from flask_socketio import send, emit
from flask_login import login_user,login_required, current_user, logout_user
# local
from app import db
from app.extensions import socketio
from app.models import User, Companies, Jobs,DirectMessages,Notifications,SimpleRepr
from datetime import datetime

from app.utils.validate_data import is_form_empty



direct_messages_bp = Blueprint("direct_messages",__name__)


# here will create the api to crud msg 


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: '+ str(json))
    socketio.emit('my response', json)


@direct_messages_bp.route("search_users/<string:input>",  methods=["GET"])
@login_required
def search_users_for_new_messages(input):
    _input = input.strip()
    if _input:
        all_users_found = User.query.filter(User.name.ilike(f"%{_input}%")).all() | Companies.query.filter(Companies.name.ilike(f"%{_input}%")).all()
        json_users = [user.__json__().get("name") for user in all_users_found]

        if len(json_users) == 0:
            return jsonify({"error": "No users found"})
        
        else:
            return jsonify({"users": json_users})

    
    return jsonify({"error": "No users found"})





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