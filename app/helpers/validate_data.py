import re
import functools

from app.models import User, Companies


def validate_register_user_data(req_data) -> list:
    errors = []

    # Required field checks with length validation
    if not req_data.get("surname"):
        errors.append("Surname is required.")
    elif len(req_data["surname"]) > 128:
        errors.append("Surname must be 128 characters or less.")

    if not req_data.get("profession"):
        errors.append("Profession is required.")
    elif len(req_data["profession"]) > 128:
        errors.append("Profession must be 128 characters or less.")
    # Check email exists in User table
    if User.query.filter_by(email=req_data.get("email")).first():
        errors.append("Email already registered as Person.")

    return errors



def validate_register_company_data(req_data) -> list:
    errors = []

    # Required field checks with length validation
    if not req_data.get('description'):
        errors.append("Description is required.")
    if not req_data.get('location'):
        errors.append("Location is required.")
    # Check email exists in Companies table
    if Companies.query.filter_by(email=req_data.get("email")).first():
        errors.append("Email already registered as Company.")
        
    return errors



def validate_register_data(req_data) -> list:
    errors = []
    # Common fields for both company and person  
    if not req_data.get("user_type"):
        errors.append("User Type is required.")
    elif req_data["user_type"].lower() not in ["company", "person"]:
        errors.append("Invalid User Type chosen.")
    elif len(req_data["user_type"]) > 8:
        errors.append("Invalid User Type chosen.")

    if not req_data.get("name"):
        errors.append("Name is required.")
    elif len(req_data["name"]) > 128:
        errors.append("Name must be 128 characters or less.")
    
    if not req_data.get("email"):
        errors.append("Email is required.")
    
    if not req_data.get("password"):
        errors.append("Password is required.")

    return errors


def validate_login_data(req_data) -> list:
    errors = []
    if not req_data.get("email"):
        errors.append("Email is required.")
    if not req_data.get("password"):
        errors.append("Password is required.")
    if  req_data.get("remember") is not None and req_data.get("remember").lower() not in ["on", "off"]:
        errors.append("Invalid value for remember.")
    if req_data.get("user_type").lower() not in ["company", "person"]:
        errors.append("Invalid User Type chosen.")
    return errors

def is_form_empty(req_data, exclude_keys=None) -> bool:
    exclude_keys = exclude_keys or []
    return not any(value for key, value in req_data.items() if key not in exclude_keys)