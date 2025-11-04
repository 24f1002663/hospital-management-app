from flask import Blueprint, render_template, session, flash, redirect, url_for
from model import db, Doctor, Patient, Appointment, User, Department
from flask import request
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
@admin_bp.route('/doctor/register', methods=['GET', 'POST'])
def register_doctor():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    
    departments= Department.query.all()

    if request.method == 'POST':
        # asking data from admin using post to register for new doctor
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        department_id=request.form.get('departmentid')
        password = request.form.get('password')
        #gettinf the department from the id and pushing the same result in specialization.
        department = Department.query.get(department_id)
        specialization = department.name if department else "Physician"

        # creating a user entry, and then adding the details and commiting
        new_user = User(
            name=name,
            email=email,
            contact=contact,
            password=password,
            role='doctor'
        )
        db.session.add(new_user)
        db.session.commit()

        # with same adding a doctor entry as it is the query of register docotr
        new_doctor = Doctor(
            id=new_user.id,
            specialization=specialization,
            departmentid=department_id
        )
        db.session.add(new_doctor)
        db.session.commit()

        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin.view_doctors'))

    # moved here from bottom (was unreachable)
    return render_template('register_doctor.html',departments=departments)


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


#now updating user details, including patients, doctors and admins
@admin_bp.route('/user/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.contact = request.form.get('contact')
        user.status = request.form.get('status')

        db.session.commit()
        flash('User details updated successfully!', 'success')
        return redirect(url_for('admin.view_users'))

    return render_template('update_user.html', user=user)

#to delete user
@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)

    # because user gets deleted then linekd doctor and patient should also
    if user.doctor:
        db.session.delete(user.doctor)
    if user.patient:
        db.session.delete(user.patient)

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

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
    doctors = User.query.filter_by(role='doctor').all()
    patients = User.query.filter_by(role='patient').all()

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
