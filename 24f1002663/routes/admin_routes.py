from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, session, flash, redirect, url_for
from model import db, Doctor, Patient, Appointment, User, Department, DoctorAvailability
from flask import request, current_app
from datetime import date, timedelta
from sqlalchemy import cast, String  # added for id search fix

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# for admin dashboard 
@admin_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    # calculating from database the numbers of doctors, patient and appointments
    total_doctors = User.query.filter_by(role="doctor").count()
    total_patients = User.query.filter_by(role="patient").count()
    total_appointments = Appointment.query.count()

    return render_template(
        'admin_dash.html',
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments
    )


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

        # hash the password before saving
        hash_password = generate_password_hash(password)

        # getting the department from the id and pushing the same result in specialization
        department = Department.query.get(department_id)
        specialization = department.name if department else "Physician"

        # creating a user entry
        new_user = User(
            name=name,
            email=email,
            contact=contact,
            password=hash_password,
            role='doctor'
        )
        db.session.add(new_user)
        db.session.commit()

        # creating doctor entry
        new_doctor = Doctor(
            id=new_user.id,
            specialization=specialization,
            departmentid=department_id
        )
        db.session.add(new_doctor)
        db.session.commit()

        # sending login mail
        try:
            from app import mail, Message
            message = Message(
                subject="Doctor Login Credentials",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            message.body = f"""
Greetings Dr. {name},

Your login credentials are:
Email: {email}
Password: {password}

login here: http://localhost:5000/auth/login
"""
            mail.send(message)
            flash(f"Doctor '{name}' added! Credentials sent.", "success")

        except:
            flash(f"Doctor '{name}' added successfully, but email not sent.", "warning")

        return redirect(url_for('admin.view_doctors'))

    return render_template('register_doctor.html', departments=departments)


# list doctors
@admin_bp.route('/doctor/view')
def view_doctors():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctors = Doctor.query.all()
    departments = Department.query.all()
    return render_template('view_doctors.html', doctors=doctors, departments=departments)


# update doctor department
@admin_bp.route('/doctor/update/<int:doctor_id>', methods=['POST'])
def update_doctor(doctor_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.get_or_404(doctor_id)
    new_dept = request.form.get('departmentid')

    if new_dept:
        department = Department.query.get(new_dept)
        doctor.departmentid = new_dept
        if department:
            doctor.specialization = department.name

    db.session.commit()
    flash('Doctor updated successfully!', 'success')
    return redirect(url_for('admin.view_doctors'))


# search doctor
@admin_bp.route('/doctor/search')
def search_doctor():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    query = request.args.get('query', '')
    doctors = Doctor.query.join(User).filter(
        (User.name.ilike(f"%{query}%")) |
        (Doctor.specialization.ilike(f"%{query}%"))
    ).all()

    return render_template('view_doctors.html', doctors=doctors, query=query)


# search patient
@admin_bp.route('/patient/search')
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
        patients = User.query.filter_by(role='patient').all()

    return render_template('view_patients.html', patients=patients, query=query)


# view users
@admin_bp.route('/users/view')
def view_users():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('view_users.html', users=users)


# manage appointments (add, update, validate)
@admin_bp.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    from datetime import datetime

    # -------------------------------
    # handle adding or updating appointment
    # -------------------------------
    if request.method == 'POST':

        appt_id = request.form.get('appointment_id')
        patientid = request.form.get('patientid')
        doctorid = request.form.get('doctorid')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        status = request.form.get('status')

        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appt_time = datetime.strptime(time_str, "%H:%M").time()

        # check doctor availability
        day_check = DoctorAvailability.query.filter_by(
            doctor_id=doctorid,
            date=appt_date
        ).first()

        if not day_check or not day_check.is_available:
            flash("Doctor is not available on this date.", "danger")
            return redirect(url_for('admin.manage_appointments'))

        # check time conflict
        conflict = Appointment.query.filter(
            Appointment.doctorid == doctorid,
            Appointment.date == appt_date,
            Appointment.time == appt_time,
            Appointment.status == "Scheduled"
        )

        if appt_id:
            conflict = conflict.filter(Appointment.id != appt_id)

        conflict = conflict.first()

        if conflict:
            flash("This doctor already has an appointment at this time.", "danger")
            return redirect(url_for('admin.manage_appointments'))

        # safe to update / add
        if appt_id:
            appt = Appointment.query.get(appt_id)
            appt.patientid = patientid
            appt.doctorid = doctorid
            appt.date = appt_date
            appt.time = appt_time
            appt.status = status
        else:
            new_appt = Appointment(
                patientid=patientid,
                doctorid=doctorid,
                date=appt_date,
                time=appt_time,
                status=status
            )
            db.session.add(new_appt)

        db.session.commit()
        flash("Appointment saved successfully!", "success")
        return redirect(url_for('admin.manage_appointments'))

    # show appointment list
    appointments = Appointment.query.all()

    doctors = User.query.join(Doctor).filter(
        User.role == 'doctor',
        User.is_blacklisted == False,
        Doctor.is_available == True
    ).all()

    patients = User.query.filter_by(role='patient', is_blacklisted=False).all()

    return render_template(
        'manage_appointments.html',
        appointments=appointments,
        doctors=doctors,
        patients=patients
    )


# delete appointment
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


# blacklist user
@admin_bp.route('/user/blacklist/<int:user_id>', methods=['POST'])
def blacklist_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.is_blacklisted = True
    db.session.commit()

    flash(f"user '{user.name}' has been blacklisted.", 'warning')
    return redirect(request.referrer or url_for('admin.dashboard'))


# unblacklist user
@admin_bp.route('/user/unblacklist/<int:user_id>', methods=['POST'])
def unblacklist_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    db.session.commit()

    flash(f"user '{user.name}' has been unblacklisted.", 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


# view doctor profile
@admin_bp.route('/doctor/profile/<int:doctor_id>')
def view_doctor_profile(doctor_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user
    department = doctor.department

    return render_template('doctor_profile.html', doctor=doctor, user=user, department=department)
