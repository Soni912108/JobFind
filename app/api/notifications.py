from flask import Blueprint, request,jsonify
from app import db
from app.models import  Notifications
from datetime import datetime
from flask_login import login_required, current_user
from app.extensions import socketio
from flask_socketio import join_room,emit

notifications_bp = Blueprint("notifications",__name__)

@notifications_bp.route("/notification/mark_read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    notification = Notifications.query.get(notification_id)
    if notification and notification.receiver_id == current_user.id:
        notification.read = True
        db.session.commit()
        return jsonify({"message": "Notification mark as read"}),200
    
    return jsonify({"error": "Notification not found"}), 404


@notifications_bp.route("/notification/delete/<int:notification_id>", methods=["POST"])
@login_required
def delete_notification(notification_id):
    notification = Notifications.query.get(notification_id)
    if notification and notification.receiver_id == current_user.id:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({"message": "Notification deleted"}),200
    
    return jsonify({"error": "Notification not found"}), 404



#socket to handle new notifications
@socketio.on("join_notifications")
def handle_join_notifications(data):
    """Handle user joining their notification room"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'User not authenticated'}, room=request.sid)
    try:
        # Get user info from data
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        
        if not user_id:
            print("Error: No user_id provided in join_notifications")
            return
        
        # Create a unique room name for user's notifications
        notification_room = f"notifications_{user_id}"
        
        # Join the room
        join_room(notification_room)
        
        print(f"User {user_id} ({user_type}) joined notification room: {notification_room}")
        
        # Optionally send confirmation
        return {"status": "success", "message": f"Joined notification room"}
        
    except Exception as e:
        print(f"Error in handle_join_notifications: {str(e)}")
        return {"status": "error", "message": str(e)}




def create_notification(receiver_id, message,emit_notification=False):
    """
    Create a new notification record.
    Optionally, if emit_notification is True, emit a real-time update.
    """
    new_notification = Notifications(
        receiver_id=receiver_id,
        message=message,
        read=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    try:
        db.session.add(new_notification)
        db.session.commit()
        print(f"Notification added to DB correctly {new_notification.id}")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None

    if emit_notification:
            notification_room = f"notifications_{receiver_id}"
            socketio.emit('new_notification', 
                         new_notification.__json__(), 
                         room=notification_room)
            print(f"Emitted notification to room: {notification_room}")
            
    return new_notification


