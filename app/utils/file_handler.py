import os
import uuid
from werkzeug.utils import secure_filename
from flask_login import current_user
from app import app

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resume(file):
    """
    Securely save uploaded resume file.
    Returns: (unique_filename, file_url) or (None, None) on failure.
    """
    if file and allowed_file(file.filename):
        # Create a secure, unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1].lower()  # get extension in lower case
        unique_filename = f"{uuid.uuid4().hex}_{current_user.get_id()}{file_extension}"
        
        # Save file to the absolute path defined in app.config['UPLOAD_FOLDER']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Generate a URL that can be used to access the file, e.g. via static folder
        file_url = f"/static/resume_upload/{unique_filename}"
        print(f"Saved file as {unique_filename}, URL: {file_url}")
        return unique_filename, file_url
    return None, None

def delete_resume(filename):
    """
    Safely delete a resume file

    If file not found than will return False - returns False if no input was given

    """
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return 0