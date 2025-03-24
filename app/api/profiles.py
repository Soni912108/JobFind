from flask import Blueprint, request, flash, redirect, url_for, jsonify,render_template
from app import db
from app.models import Person, Company, User
from datetime import datetime
from flask_login import login_required, current_user

profiles_bp = Blueprint("profiles", __name__)

# here will add rest api to edit profile

# endpoint to show profile to visitors
@profiles_bp.route("/view/<int:user_id>", methods=["GET"])
@login_required
def visit_profile(user_id):
    # Find the user by ID
    user = User.query.get_or_404(user_id)
    
    # If user wants to see their own profile, redirect to profile page
    if user_id == current_user.id:
        return redirect(url_for('frontend.profile'))
    
    # Prepare the base user data
    user_data = {
        'name': user.name,
        'email': user.email,
        'location': user.location or 'No location set',
        'user_type': user.user_type
    }
    
    # Add type-specific data
    if isinstance(user, Person):
        user_data.update({
            'surname': user.surname,
            'profession': user.profession or 'Not specified',
            'skills': user.skills or [],
            'experience': user.experience or [],
            'current_company_info': user.current_company_info or {}
        })
        template = 'profile/visit_person_profile.html'
        
    elif isinstance(user, Company):
        user_data.update({
            'description': user.description or 'No description available',
            'social_links': user.social_links or {}
        })
        template = 'profile/visit_company_profile.html'
    
    return render_template(
        template,
        user=current_user,
        user_data=user_data,
        is_person=isinstance(user, Person),
        is_company=isinstance(user, Company)
    )


# edit profile
@profiles_bp.route("/edit/<int:user_id>", methods=["POST"])
@login_required
def edit_profile(user_id):
    # Only allow users to edit their own profile
    if user_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': 'You can only edit your own profile'
        }), 403
    
    try:
        data = request.json
        user = User.query.get_or_404(user_id)
        
        # Update common fields
        if 'name' in data:
            user.name = data['name']
        if 'location' in data:
            user.location = data['location']
            
        # Update type-specific fields
        if isinstance(user, Person):
            if 'surname' in data:
                user.surname = data['surname']
            if 'profession' in data:
                user.profession = data['profession']
            if 'skills' in data:
                # Ensure skills is a list
                user.skills = data['skills'] if isinstance(data['skills'], list) else []
            if 'experience' in data:
                # Ensure experience is a list of dictionaries
                if isinstance(data['experience'], list):
                    user.experience = [
                        {
                            'title': exp.get('title', ''),
                            'company': exp.get('company', ''),
                            'description': exp.get('description', ''),
                            'start_date': exp.get('start_date', ''),
                            'end_date': exp.get('end_date', '')
                        }
                        for exp in data['experience']
                    ]
            if 'current_company_info' in data:
                # Ensure it's a dictionary with required fields
                if isinstance(data['current_company_info'], dict):
                    user.current_company_info = {
                        'company': data['current_company_info'].get('company', ''),
                        'title': data['current_company_info'].get('title', ''),
                        'description': data['current_company_info'].get('description', '')
                    }
                    
        elif isinstance(user, Company):
            if 'description' in data:
                user.description = data['description']
            if 'social_links' in data:
                # Ensure social_links is a dictionary
                if isinstance(data['social_links'], dict):
                    user.social_links = data['social_links']
        
        # Update the updated_at timestamp
        user.updated_at = datetime.now()
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
