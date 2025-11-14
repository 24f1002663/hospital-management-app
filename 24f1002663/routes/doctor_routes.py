from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from model import db, Appointment, Treatment, Prescription, Patient, User, Doctor,DoctorAvailability
from datetime import date, timedelta

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')
# Doctor Dashboard 
@doctor_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)
    today = date.today()
##we did this to automatically update availability
    for i in range(7):
        day = today + timedelta(days=i)
        existing = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=day).first()
        if not existing:
            new = DoctorAvailability(doctor_id=doctor_id, date=day, is_available=True)
            db.session.add(new)
    db.session.commit()

    appointments = Appointment.query.filter(
        Appointment.doctorid == doctor_id,
        Appointment.status.notin_(["Completed"]),
        Appointment.date >= today
    ).order_by(Appointment.date, Appointment.time).all()

    next_7_days = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today
    ).order_by(DoctorAvailability.date.asc()).limit(7).all()

    # adding next 7 days to the render the template call:
    return render_template(
        'doctor_dash.html',
        doctor=doctor,
        appointments=appointments,
        next_7_days=next_7_days,  
        today=today,
        timedelta=timedelta
    )
#for toggle the availability
@doctor_bp.route('/toggle_availability', methods=['POST'])
def toggle_availability():
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)

    doctor.is_available = not doctor.is_available
    db.session.commit()

    flash(f"You are now {'Available' if doctor.is_available else 'Unavailable'}.", 'success')
    return redirect(url_for('doctor.dashboard'))
#for enterining the presciption i.e treatment
@doctor_bp.route('/treatment/<int:appointment_id>', methods=['GET', 'POST'])
def treatment(appointment_id):
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    appointment = Appointment.query.get_or_404(appointment_id)
    patient = appointment.patient
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)  # ✅ get the doctor info

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        procedure = request.form.get('procedure')
        medication = request.form.get('medication')

        treatment = Treatment(
            patientid=appointment.patientid,
            doctorid=appointment.doctorid,
            diagnosis=diagnosis,
            procedure=procedure,
            date=date.today()
        )
        db.session.add(treatment)
        db.session.commit()

        prescription = Prescription(
            treatmentid=treatment.id,
            medication=medication
        )
        db.session.add(prescription)
        db.session.commit()

        #to automark if the prescription is written
        appointment.status = "Completed"
        db.session.commit()

        flash('Treatment and prescription saved successfully!', 'success')
        return redirect(url_for('doctor.dashboard'))

    # pass doctor to the template
    return render_template('doctor_treatment.html', appointment=appointment, patient=patient, doctor=doctor)

# FOR viewing the patient's medical history
@doctor_bp.route('/patient/history/<int:patient_id>')
def view_patient_history(patient_id):
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    treatments = Treatment.query.filter_by(patientid=patient_id).all()
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)

    from datetime import datetime
    viewed_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # current date/time

    return render_template(
        'patient_history.html',
        treatments=treatments,
        doctor=doctor,
        viewed_on=viewed_on
    )

# update the appoitment status
@doctor_bp.route('/appointment/update/<int:appointment_id>', methods=['POST'])
def update_appointment_status(appointment_id):
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    appointment = Appointment.query.get_or_404(appointment_id)
    new_status = request.form.get('status')

    appointment.status = new_status
    db.session.commit()

    flash('Appointment status updated successfully!', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/past_appointments')
def past_appointments():
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)

    # Get completed and cancelled appointments
    past_appointments = Appointment.query.filter(
        Appointment.doctorid == doctor_id,
        Appointment.status.in_(["Completed", "Cancelled"])
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()

    return render_template('doctor_past_appointments.html', doctor=doctor, past_appointments=past_appointments)
@doctor_bp.route('/update_availability', methods=['POST'])
def update_availability():
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    doctor_id = session.get('user_id')
    selected_ids = request.form.getlist('available_days')  

    availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
    for a in availabilities:
        a.is_available = str(a.id) in selected_ids

    db.session.commit()
    flash(' Availability schedule updated successfully!', 'success')
    return redirect(url_for('doctor.dashboard'))