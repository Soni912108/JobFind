from flask import Blueprint, request, render_template,flash, redirect, url_for,jsonify,session
from flask_socketio import send, emit,join_room,rooms  
from flask_login import login_user,login_required, current_user, logout_user
# local
from app import db
from app.extensions import socketio
from app.models import User, Companies, Jobs,DirectMessages,Notifications,SimpleRepr,Rooms
from datetime import datetime
from .notifications import create_notification
from app.utils.validate_data import is_form_empty
import json



direct_messages_bp = Blueprint("direct_messages",__name__)


# create new room
@direct_messages_bp.route("room/new",  methods=["POST"])
@login_required
def new_room():
    print(request.form)
    # validate the form
    if is_form_empty(request.form):
        flash("Missing data, please fill out the form", "warning")

    try:
        # check if the user is a Company/User - to get the name
        room_owner_name = User.query.filter(User.id == current_user.id).first().name
        if room_owner_name is None:
            room_owner_name =  Companies.query.filter(Companies.id == current_user.id).first().name
            other_user_type = "Company"

        new_room = Rooms(
            name = request.form.get("name"),
            room_owner_id = current_user.id,
            room_owner_name= room_owner_name,
            room_owner_type= "Person" if User.query.filter(User.id == current_user.id).first() else "Company",
            other_user_id = request.form.get("other_user_id"),
            other_user_type =other_user_type
        )
        db.session.add(new_room)
        db.session.commit()

        flash("Room created successfully", "success")
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        print("Error creating room:", str(e))
        flash("Error creating room", "danger")
        return jsonify({"success": False, "message": str(e)})



# join a existing room(in which the user is part of)
@direct_messages_bp.route("room/join/<int:room_id>",  methods=["POST"])
@login_required
def join_room(room_id):
    try:
        # Get the room and verify user has access
        room = Rooms.query.get_or_404(room_id)

        # Check if current user is in the room
        if str(current_user.id) not in [str(room.room_owner_id), str(room.other_user_id)]:
            flash("You don't have access to this room", "danger")
            return redirect(url_for('frontend.rooms'))

        # Get all messages for this room
        messages = DirectMessages.query.filter_by(room_id=room_id).order_by(DirectMessages.created_at.asc()).all()

        return render_template(
            "dms/messages.html",
            room=room,
            messages=messages,
            other_user=room.other_user_id,
            room_owner=room.room_owner_id,
            room_owner_name=room.room_owner_name,
            user=current_user
        )

    except Exception as e:
        print("Error joining room:", str(e))
        flash("Error accessing room", "danger")
        return redirect(url_for('frontend.rooms'))

    





# here will create the api to crud msg 
# def get_private_room(user1_id, user2_id):
#     try:
#         # Convert both IDs to integers for comparison
#         user1_int = int(user1_id)
#         user2_int = int(user2_id)
        
#         # Sort the IDs
#         sorted_ids = sorted([user1_int, user2_int])
#         return f"private_{sorted_ids[0]}_{sorted_ids[1]}"
#     except ValueError as e:
#         print(f"Error converting IDs to integers: {e}")
#         return None


# @socketio.on('connect')
# def handle_connect():
#     if not current_user.is_authenticated:
#         return False
    
#     try:
#         # Get all rooms where current user is either sender or receiver
#         messages = DirectMessages.query.filter(
#             (DirectMessages.sender_id == current_user.id) | 
#             (DirectMessages.receiver_id == current_user.id)
#         ).order_by(DirectMessages.created_at.desc()).all()
        
#         # Create a dict to store unique conversations with their latest message
#         conversations = {}
#         for msg in messages:
#             room = msg.room
#             if room not in conversations:
#                 # Determine the other user in the conversation
#                 other_user_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
#                 other_user_type = msg.receiver_type if msg.sender_id == current_user.id else msg.sender_type
                
#                 # Get other user's info
#                 other_user = (Companies.query.get(other_user_id) if other_user_type == 'Company' 
#                             else User.query.get(other_user_id))
                
#                 if other_user:
#                     conversations[room] = {
#                         'room': room,
#                         'other_user_id': other_user_id,
#                         'other_user_name': other_user.name,
#                         'other_user_type': other_user_type,
#                         'last_message': msg.message,
#                         'last_message_time': msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                         'unread_count': 0
#                     }
        
#         # Emit conversations list
#         socketio.emit('conversations_list', {'conversations': list(conversations.values())}, room=request.sid)
        
#     except Exception as e:
#         print(f"Error loading conversations: {e}")
#         return False

#     return True



# @socketio.on('join private')
# def handle_join_private(data):
#     receiver_id = data.get('receiver_id')
#     if not receiver_id:
#         return
        
#     # Get receiver info
#     receiver = User.query.get(receiver_id) or Companies.query.get(receiver_id)
#     if not receiver:
#         return
        
#     room = get_private_room(current_user.id, receiver_id)
#     join_room(room)

#     try:
#         # Fetch conversation history
#         messages = DirectMessages.query.filter_by(room=room).order_by(DirectMessages.created_at.asc()).all()
#         messages_json = []
        
#         for msg in messages:
#             msg_dict = msg.__json__()
#             # Add sender info to each message
#             sender = User.query.get(msg.sender_id) or Companies.query.get(msg.sender_id)
#             msg_dict['sender_name'] = sender.name if sender else 'Unknown'
#             msg_dict['sender_type'] = msg.sender_type
#             messages_json.append(msg_dict)
            
#         # Emit conversation data
#         socketio.emit('conversation_data', {
#             'room': room,
#             'messages': messages_json,
#             'receiver_name': receiver.name,
#             'receiver_id': receiver.id
#         }, room=request.sid)
        
#     except Exception as e:
#         print(f"Error on join private event: {e}")




# @socketio.on('private message')
# def handle_private_message(data):
#     print(f"data in handle_private_message: {data}")
#     receiver_id = data.get('receiver_id')
#     message = data.get('message', '')
#     if not receiver_id:
#         socketio.emit('private message', {"error": "No user to send message to"}, room=request.sid)
#         return
#     if current_user.id == receiver_id:
#         socketio.emit('private message', {"error": "You cannot message yourself"}, room=request.sid)
#         return
#     # Check if receiver exists in the DB
#     user_receiver = User.query.get(receiver_id) or Companies.query.get(receiver_id)
#     if not user_receiver:
#         socketio.emit('private message', {"error": "Receiver does not exist"}, room=request.sid)
#         return

#     room = get_private_room(current_user.id, receiver_id)
#     # Store the message in the DB
#     dm = DirectMessages(
#         sender_id=current_user.id,
#         sender_type=current_user.user_type,
#         receiver_id=receiver_id,
#         receiver_type="Company" if Companies.query.get(receiver_id) else "User",
#         message=message,
#         room=room,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
#     try:
#         db.session.add(dm)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         print(f"Database error: {e}")
#         socketio.emit('private message', {"error": "Message could not be saved"}, room=request.sid)
#         return

#     # Create a notification for the receiver
#     notif_message = f"You received a new message from {current_user.name}"
#     create_notification(receiver_id, notif_message, emit_notification=True)

#     # Emit the new message to the room so both participants receive it
#     socketio.emit('private message', {
#         'sender_id': current_user.id,
#         'sender_name': current_user.name,
#         'message': message,
#         'room': room,
#         'created_at': dm.created_at.strftime("%Y-%m-%d %H:%M:%S")
#     }, room=room)



@direct_messages_bp.route("search_users/<string:input>",  methods=["GET"])
@login_required
def search_users_for_new_messages(input):
    _input = input.strip()
    print(_input)
    if _input:
        # first check the users table for the given name - Note: name is not unique in this table
        all_users_found = User.query.filter(User.name.ilike(f"%{_input}%")).all()
        if len(all_users_found) != 0:
            json_users = [user.__json__() for user in all_users_found]
            users_only_id_and_name_info = [(user["id"], user["name"]) for user in json_users]
            return jsonify({"users" : users_only_id_and_name_info})

        # search the company table
        all_companies_found = Companies.query.filter(Companies.name.ilike(f"%{_input}%")).all()
        if len(all_companies_found) != 0:
            companies_json = [company.__json__() for company in all_companies_found]
            companies_only_id_and_name_info = [(company["id"], company["name"]) for company in companies_json]
            return jsonify({"users" : companies_only_id_and_name_info})
        
        return jsonify({"error": "No data found for this search input"})
    
    return jsonify({"error": "No data found for this search input"})


