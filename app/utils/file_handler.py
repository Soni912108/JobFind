from werkzeug.utils import secure_filename
from flask_login import current_user
import os
import uuid

from app import app

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_resume(file):
    """
    Securely save uploaded resume file.
    Returns: (unique_filename, file_url) or (None, None) on failure.
    """
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{current_user.get_id()}{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        file_url = f"/static/resume_upload/{unique_filename}"
        print(f"Saved file as {unique_filename}, URL: {file_url}")
        return unique_filename, file_url
    return None, None


def delete_resume(filename):
    """
    Safely delete a resume file.
    Returns True if deleted, False if file not found.
    """
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    return False

    