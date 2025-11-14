from flask import Blueprint, render_template, request, redirect, url_for, flash, session
#we import blueprint because it organizes in separate components,flash to store data like user role 
from model import db, User, Patient
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
#we create blueprint names auth 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        # added blacklist so that user cannot login 
        if user and user.is_blacklisted:
            flash("Your account has been blacklisted. Please contact the admin.", "danger")
            return redirect(url_for('auth.login'))

        if user and check_password_hash(user.password, password):
            # normalize role to lowercase
            role = user.role.lower()
            session['user_role'] = role
            session['user_id']=user.id
            flash(f'{role.capitalize()} logged in!', 'success')

            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            else:
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')


#for new users to sign up 
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        dob = request.form['dob']
        gender = request.form['gender']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.Please head towards login','warning')
            return redirect(url_for('auth.login'))
        
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            contact=contact,
            role='patient'
        )
        db.session.add(new_user)
        db.session.commit()

        new_patient=Patient(
            id=new_user.id,
            dob=date.fromisoformat(dob),
            gender=gender
        )
        db.session.add(new_patient)
        db.session.commit()

        flash('Patient registered succesfully, now can login','success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))
