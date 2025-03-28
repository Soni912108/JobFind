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
    print(user_data)
    return render_template(
        template,
        user=current_user,
        user_data=user_data,
        is_person=isinstance(user, Person),
        is_company=isinstance(user, Company)
    )


# 1. Basic Profile Edit (shared data)
@profiles_bp.route("/edit/basic/<int:user_id>", methods=["POST"])
@login_required
def edit_basic_profile(user_id):
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
        if 'email' in data:
            user.email = data['email']
            
        # Person-specific basic fields
        if isinstance(user, Person) and 'surname' in data:
            user.surname = data['surname']
        if isinstance(user, Person) and 'profession' in data:
            user.profession = data['profession']
            
        user.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Basic profile information updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 2. Company Social Links
@profiles_bp.route("/edit/social-links/<int:user_id>", methods=["POST"])
@login_required
def edit_social_links(user_id):
    if user_id != current_user.id or not isinstance(current_user, Company):
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access'
        }), 403
    
    try:
        data = request.json
        company = Company.query.get_or_404(user_id)
        
        if 'social_links' in data and isinstance(data['social_links'], dict):
            company.social_links = data['social_links']
            company.updated_at = datetime.now()
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Social links updated successfully'
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# NOTE: need a function to add experiences

# 3. Person Professional Info
@profiles_bp.route("/edit/professional/<int:user_id>", methods=["POST"])
@login_required
def edit_professional_info(user_id):
    if user_id != current_user.id or not isinstance(current_user, Person):
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access'
        }), 403
    
    try:
        data = request.json
        person = Person.query.get_or_404(user_id)
        
        # Handle skills update
        if 'skills' in data:
            if isinstance(data['skills'], list):
                person.skills = data['skills']
        
        # Handle experience update
        if 'experience' in data:
            if isinstance(data['experience'], list):
                # list comprehension 
                all_experience = [
                    {
                        'title': exp.get('title', ''),
                        'company': exp.get('company', ''),
                        'description': exp.get('description', ''),
                        'start_date': exp.get('start_date', ''),
                        'end_date': exp.get('end_date', '')
                    }
                    for exp in data['experience']
                ]
                print(f"All experiences: {all_experience}")
                person.experience = all_experience
        
        # Handle current company info update
        if 'current_company_info' in data:
            if isinstance(data['current_company_info'], dict):
                person.current_company_info = {
                    'company': data['current_company_info'].get('company', ''),
                    'title': data['current_company_info'].get('title', ''),
                    'description': data['current_company_info'].get('description', '')
                }
        
        person.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Professional information updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
