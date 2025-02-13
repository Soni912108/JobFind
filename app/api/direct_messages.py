from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_socketio import send, emit, join_room, rooms
from flask_login import login_required, current_user
from datetime import datetime
# local
from app import db
from app.extensions import socketio
from app.models import User, Person, Company, Room, Message
from .notifications import create_notification
from app.utils.validate_data import is_form_empty, validate_new_room_data

direct_messages_bp = Blueprint("direct_messages", __name__)

@direct_messages_bp.route("room/new", methods=["POST"])
@login_required
def new_room():
    try:
        # Validate form data
        if is_form_empty(request.form):
            flash("Missing data, please fill out the form", "warning")
            return jsonify({"success": False, "message": "Missing data"})

        errors = validate_new_room_data(request.form)
        if errors:
            for error in errors:
                flash(error, "warning")
            return jsonify({"success": False, "message": "Validation errors"})

        # Get the other user from the unified User table
        other_user_id = request.form.get("other_user_id")
        other_user = User.query.get(other_user_id)
        
        if not other_user:
            flash("Invalid other user", "danger")
            return jsonify({"success": False, "message": "Invalid other user"})

        # Create new room with simplified structure
        new_room = Room(
            name=request.form.get("name"),
            owner_id=current_user.id,
            other_user_id=other_user.id,
            is_active=True
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

@direct_messages_bp.route("room/join/<int:room_id>", methods=["POST"])
@login_required
def join_room_route(room_id):
    try:
        if not room_id:
            return jsonify({"error": "Room not found"}), 404

        # Get room and check authorization
        room = Room.query.filter(
            Room.id == room_id,
            db.or_(
                Room.owner_id == current_user.id,
                Room.other_user_id == current_user.id
            )
        ).first()

        if not room:
            flash("Room not found or access denied", "danger")
            return jsonify({"error": "Room not found"}), 404

        # Get other participant's info using the helper method
        other_participant = room.get_other_participant(current_user.id)
        is_room_owner = current_user.id == room.owner_id

        # Get messages for this room
        messages = Message.query.filter_by(room_id=room_id)\
                              .order_by(Message.created_at.asc())\
                              .all()

        return render_template(
            "dms/messages.html",
            room=room,
            messages=messages,
            other_user=other_participant.id,
            other_user_name=other_participant.name,
            other_user_type=other_participant.user_type,
            is_room_owner=is_room_owner,
            user=current_user
        )
    except Exception as e:
        print(f"Error joining room: {str(e)}")
        flash("Error accessing room", "danger")
        return redirect(url_for('frontend.rooms'))

@direct_messages_bp.route("search_users/<string:input>", methods=["GET"])
@login_required
def search_users_for_new_messages(input):
    _input = input.strip()
    if _input:
        # Search in unified User table
        users_found = User.query.filter(
            db.and_(
                User.name.ilike(f"%{_input}%"),
                User.id != current_user.id  # Don't include current user
            )
        ).all()
        
        if users_found:
            users_info = [(user.id, user.name) for user in users_found]
            return jsonify({"users": users_info})
        
        return jsonify({"error": "No users found for this search input"})
    
    return jsonify({"error": "No search input provided"})


# socket to listen for new messages
@socketio.on('join')
def on_join(data):
    if not current_user.is_authenticated:
        return False
    
    room = data.get('room')
    if room:
        join_room(room)
        print(f"User {current_user.id} joined room {room}")  # Debug log
        return True
    return False


@socketio.on('new message')
def new_message(data):
    if not current_user.is_authenticated:
        return False

    try:
        room_id = data.get('room_id')
        message_text = data.get('message')

        print(f"Received message in room {room_id}: {message_text}")  # Debug log

        if not room_id or not message_text or not message_text.strip():
            return False

        # Verify room access
        room = Room.query.filter(
            Room.id == room_id,
            db.or_(
                Room.owner_id == current_user.id,
                Room.other_user_id == current_user.id
            )
        ).first()

        if not room: return False

        # Create new message
        message = Message(
            room_id=room_id,
            sender_id=current_user.id,
            message=message_text.strip()
        )
        
        try:
            db.session.add(message)
            db.session.commit()
            print(f"Message created successfully: {message.id}")  # Debug log
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            db.session.rollback()
            return False

        # Get other participant for notification
        other_participant = room.get_other_participant(current_user.id)
        
        message_data = {
            'sender_id': current_user.id,
            'sender_name': current_user.name,
            'message': message_text,
            'created_at': message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"Prepared message data: {message_data}")  # Debug log

        try:
            emit('new message', message_data, room=str(room_id),include_self=False)
            print(f"Message emitted successfully to room {room_id}")  # Debug log
        except Exception as emit_error:
            print(f"Emit error: {str(emit_error)}")
            return False

        # Create notification for other participant if they're not in the room
        if str(room_id) not in rooms(other_participant.id):
            try:
                notif_message = f"New message from {current_user.name}"
                create_notification(other_participant.id, notif_message, emit_notification=True)
                print(f"Notification created for user {other_participant.id}")  # Debug log
            except Exception as notif_error:
                print(f"Notification error: {str(notif_error)}")

        return True

    except Exception as e:
        import traceback
        print(f"Error handling new message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # Full traceback
        db.session.rollback()
        return False



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



