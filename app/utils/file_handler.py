import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename
from flask_login import current_user


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_resume(file):
    """
    Securely save uploaded resume file.
    Returns: unique_filename or None on failure.
    """
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{current_user.get_id()}{file_extension}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        current_app.logger.info(f"Saved file as {unique_filename}")
        return unique_filename
    return None


def delete_resume(filename):
    """
    Safely delete a resume file.
    Returns True if deleted, False if file not found.
    """
    if filename:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            current_app.logger.warning(f"Removed resume {file_path} form disk")
            os.remove(file_path)
            return True
    return False

    