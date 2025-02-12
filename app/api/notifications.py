from flask import Blueprint, request, flash, redirect, url_for
from app import db
from app.models import User, Company, Notifications,JobApplication
from datetime import datetime
from flask_login import login_user,login_required, current_user, logout_user

notifications_bp = Blueprint("notifications",__name__)

@notifications_bp.route("/notification/mark_read/<int:notif_id>", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    notif = Notifications.query.get(notif_id)
    if notif and notif.receiver_id == current_user.id:
        notif.read = True
        db.session.commit()
    return redirect(url_for("frontend.notifications"))




def create_notification(receiver_id, message, emit_notification=False):
    """
    Create a new notification record.
    Optionally, if emit_notification is True, emit a real-time update.
    """
    new_notif = Notifications(
        receiver_id=receiver_id,
        message=message,
        read=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    try:
        db.session.add(new_notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None

    # Optionally emit a socket event for real-time notification update.
    if emit_notification:
        from app.extensions import socketio  # import socketio if not already imported
        socketio.emit('new_notification', new_notif.__json__(), room=f"user_{receiver_id}")
    return new_notif
