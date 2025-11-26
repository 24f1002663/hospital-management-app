from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from model import db, User, Doctor, Appointment, Treatment, Prescription, DoctorAvailability, Patient
from datetime import date, datetime

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


# patient dashboard
@patient_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    patient_id = session.get('user_id')

    upcoming = Appointment.query.filter(
    Appointment.patientid == patient_id,
    Appointment.date >= date.today(),
    Appointment.status != "Completed"
).order_by(Appointment.date, Appointment.time).all()


    past = Appointment.query.filter(
    Appointment.patientid == patient_id,
    Appointment.status == "Completed"
).order_by(Appointment.date.desc()).all()


    return render_template(
        'patient_dash.html',
        upcoming=upcoming,
        past=past
    )


# view doctors
@patient_bp.route('/doctors', methods=['GET'])
def view_doctors():
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    query = request.args.get('query', '').strip()

    doctors = Doctor.query.join(User).filter(
        User.is_blacklisted == False,
        Doctor.is_available == True,
        (
            (User.name.ilike(f"%{query}%")) |
            (Doctor.specialization.ilike(f"%{query}%"))
        )
    ).all()

    return render_template('patient_view_doctors.html', doctors=doctors, query=query)


# book appointment
@patient_bp.route('/appointment/book', methods=['GET', 'POST'])
def book_appointment():
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    patient_id = session.get('user_id')
    doctor_id_from_url = request.args.get('doctorid')

    doctors = Doctor.query.join(User).filter(
        User.is_blacklisted == False,
        Doctor.is_available == True
    ).all()

    if request.method == 'POST':
        doctorid = request.form.get('doctorid')
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appt_time = datetime.strptime(time_str, "%H:%M").time()

        day_check = DoctorAvailability.query.filter_by(
            doctor_id=doctorid,
            date=appt_date
        ).first()

        if not day_check or not day_check.is_available:
            flash("Doctor is not available on this date.", "danger")
            return redirect(url_for('patient.book_appointment'))

        conflict = Appointment.query.filter_by(
            doctorid=doctorid,
            date=appt_date,
            time=appt_time,
            status="Scheduled"
        ).first()

        if conflict:
            flash("This time slot is already booked.", "danger")
            return redirect(url_for('patient.book_appointment'))

        new_appt = Appointment(
            patientid=patient_id,
            doctorid=doctorid,
            date=appt_date,
            time=appt_time,
            status="Scheduled"
        )
        db.session.add(new_appt)
        db.session.commit()

        flash("Appointment booked!", "success")
        return redirect(url_for('patient.dashboard'))

    return render_template(
        'patient_book_appointment.html',
        doctors=doctors,
        doctorid=doctor_id_from_url
    )


# view full history for a single appointment
@patient_bp.route('/history/<int:appointment_id>')
def view_single_history(appointment_id):
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patientid != session.get('user_id'):
        flash("Not allowed.", "danger")
        return redirect(url_for('patient.dashboard'))

    treatments = Treatment.query.filter_by(
        patientid=appointment.patientid,
        doctorid=appointment.doctorid
    ).all()

    return render_template(
        'patient_history_single.html',
        appointment=appointment,
        treatments=treatments
    )


# cancel appointment
@patient_bp.route('/appointment/cancel/<int:appt_id>', methods=['POST'])
def cancel_appointment(appt_id):
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    appt = Appointment.query.get_or_404(appt_id)

    if appt.patientid != session.get('user_id'):
        flash("Not allowed.", 'danger')
        return redirect(url_for('patient.dashboard'))

    appt.status = "Cancelled"
    db.session.commit()

    flash("Appointment cancelled.", "success")
    return redirect(url_for('patient.dashboard'))


# patient profile
@patient_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    patient = Patient.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.contact = request.form.get('contact')
        patient.dob = request.form.get('dob')
        patient.gender = request.form.get('gender')

        new_pass = request.form.get('password')
        if new_pass.strip():
            user.password = new_pass

        patient.dob = date.fromisoformat(request.form['dob'])
        patient.gender = request.form['gender']

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('patient.profile'))

    return render_template('patient_profile.html', user=user, patient=patient)
@patient_bp.route('/doctor/<int:doctor_id>/availability')
def view_doctor_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id).order_by(DoctorAvailability.date).all()
    return render_template('doctor_availability.html', doctor=doctor, availability=availability)
