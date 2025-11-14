from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, session, flash, redirect, url_for
from model import db, Doctor, Patient, Appointment, User, Department
from flask import request,current_app
from sqlalchemy import cast, String  # added for id search fix
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
#for admin dashboard 
@admin_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    # calculating from database the numbers of doctors, patient and appointments
    total_doctors = User.query.filter_by(role="doctor").count()
    total_patients = User.query.filter_by(role="patient").count()
    total_appointments = Appointment.query.count()

    # and passing the result in html 
    return render_template(
        'admin_dash.html',
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments
    )


# registering new doctor by admin
# registering new doctor by admin
@admin_bp.route('/doctor/register', methods=['GET', 'POST'])
def register_doctor():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    
    departments = Department.query.all()

    if request.method == 'POST':
        # asking data from admin using post to register for new doctor
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        department_id = request.form.get('departmentid')
        password = request.form.get('password')

        # ✅ hash the password before saving
        hash_password = generate_password_hash(password)

        # getting the department from the id and pushing the same result in specialization.
        department = Department.query.get(department_id)
        specialization = department.name if department else "Physician"

        # creating a user entry, and then adding the details and committing
        new_user = User(
            name=name,
            email=email,
            contact=contact,
            password=hash_password,   # ✅ store hashed password instead of plain
            role='doctor'
        )
        db.session.add(new_user)
        db.session.commit()

        # with same adding a doctor entry as it is the query of register doctor
        new_doctor = Doctor(
            id=new_user.id,
            specialization=specialization,
            departmentid=department_id
        )
        db.session.add(new_doctor)
        db.session.commit()

        #for sending the email automatically to the newly registered docotor
        try:
            from app import mail,Message
            message = Message(
                subject="Doctor Login Credentials",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            message.body = f"""
Greetings Dr. {name},
Welcome to the Hospital!

Your login credentials are:
Email: {email}
Password: {password}

Link to login: http://localhost:5000/auth/login

Regards,
Admin
"""
            mail.send(message)
            flash(f"Doctor '{name}' added! Credentials sent.", "success")

        except Exception as e:
            current_app.logger.exception("Email failed")
            flash(f"Doctor '{name}' added successfully, but email not sent.", "warning")

        return redirect(url_for('admin.view_doctors'))

    # moved here from bottom (was unreachable)
    return render_template('register_doctor.html', departments=departments)


# view doctors is for the list of all doctors to view then and then update them further
@admin_bp.route('/doctor/view')
def view_doctors():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
        
    doctors = Doctor.query.all()
    departments = Department.query.all()
    return render_template('view_doctors.html', doctors=doctors, departments=departments)


# we add this functionality of update the doctor their departments and specialization specifically.
@admin_bp.route('/doctor/update/<int:doctor_id>', methods=['POST'])
def update_doctor(doctor_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.get_or_404(doctor_id)
    new_departmentid=request.form.get('departmentid')

    if new_departmentid:
        department = Department.query.get(new_departmentid)
        doctor.departmentid = new_departmentid
        if department:
            doctor.specialization = department.name

    db.session.commit()
    flash('Doctor updated successfully!', 'success')
    return redirect(url_for('admin.view_doctors'))


# adding the functionality to search doctor
@admin_bp.route('/doctor/search', methods=['GET'])
def search_doctor():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    query = request.args.get('query', '')
    #using the 
    doctors = Doctor.query.join(User).filter(
        #this ilike is case insensitve to match anything between %
        (User.name.ilike(f"%{query}%")) | 
        (Doctor.specialization.ilike(f"%{query}%"))
    ).all()
    return render_template('view_doctors.html', doctors=doctors, query=query)


# search patient here from all the patients shown
@admin_bp.route('/patient/search', methods=['GET'])
def search_patient():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    query = request.args.get('query', '').strip()

    if query:
        patients = User.query.filter(
            (User.role == 'patient') &
            (
                (User.name.ilike(f"%{query}%")) |
                (cast(User.id, String).ilike(f"%{query}%")) |
                (User.contact.ilike(f"%{query}%"))
            )
        ).all()
    else:
        # show all patients when no query is performed
        patients = User.query.filter_by(role='patient').all()

    return render_template('view_patients.html', patients=patients, query=query)

# to delete doctor we add this
@admin_bp.route('/doctor/delete/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.get_or_404(doctor_id)
    user = User.query.get(doctor.id)  
    # delete linked user too from the user db

    # delete doc and user both 
    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    db.session.commit()

    flash('Doctor removed successfully!', 'success')
    return redirect(url_for('admin.view_doctors'))


    # code to view all users
@admin_bp.route('/users/view')
def view_users():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('view_users.html', users=users)

# to show all the appointments
@admin_bp.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    
    # we import date and time to further add and update appointments
    from datetime import datetime


    #for adding or updateing appoints
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        patientid = request.form.get('patientid')
        doctorid = request.form.get('doctorid')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        status = request.form.get('status')

        # if all fields are not fullfilled by user use 
        if not all([patientid, doctorid, date_str, time_str, status]):
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('admin.manage_appointments'))

        # now we will convert the string to th date and time format
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return redirect(url_for('admin.manage_appointments'))

        # if already an appointment is scheduled to upate that 
        if appointment_id: 
            appointment = Appointment.query.get(appointment_id)
            if appointment:
                appointment.patientid = patientid
                appointment.doctorid = doctorid
                appointment.date = date
                appointment.time = time
                appointment.status = status
                db.session.commit()
                flash('Appointment updated successfully!', 'success')
        else:  # if not then add the new appointment
            new_appointment = Appointment(
                patientid=patientid,
                doctorid=doctorid,
                date=date,
                time=time,
                status=status
            )
            db.session.add(new_appointment)
            db.session.commit()
            flash('New appointment added successfully!', 'success')

        return redirect(url_for('admin.manage_appointments'))

    # lastly display all the appointments
    appointments = Appointment.query.all()
    doctors = (User.query.join(Doctor).filter(User.role == 'doctor',User.is_blacklisted == False,Doctor.is_available == True).all())
    patients = User.query.filter_by(role='patient',is_blacklisted=False).all()

    return render_template(
        'manage_appointments.html',
        appointments=appointments,
        doctors=doctors,
        patients=patients
    )


@admin_bp.route('/appointment/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('admin.manage_appointments'))

# now we write a code to blacklist the user
@admin_bp.route('/user/blacklist/<int:user_id>', methods=['POST'])
def blacklist_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger'); return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f"User '{user.name}' has been blacklisted.", 'warning')
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/user/unblacklist/<int:user_id>', methods=['POST'])
def unblacklist_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger'); return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f"User '{user.name}' has been unblacklisted.", 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))

# to view individual doctor profile
@admin_bp.route('/doctor/profile/<int:doctor_id>')
def view_doctor_profile(doctor_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user  # get related user info
    department = doctor.department  # department info

    return render_template('doctor_profile.html', doctor=doctor, user=user, department=department)


