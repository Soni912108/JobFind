from flask import Blueprint, request, flash, redirect, url_for,jsonify
from app import db
from app.models import User, Company, Notifications,JobApplication
from datetime import datetime
from flask_login import login_required, current_user
from app.extensions import socketio


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



def create_notification(receiver_id, message, room_id,emit_notification=False):
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

    # Optionally emit a socket event for real-time notification update.
    if emit_notification:
        socketio.emit('new_notification', new_notification.__json__(), room=room_id)
    return new_notification
