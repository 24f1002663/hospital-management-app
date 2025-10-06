from app import app, db
from model import User, Department, Doctor, Patient, Appointment, Treatment, Prescription
from datetime import date, time

with app.app_context():
    #first adding the departments
    dept1 = Department(name="Cardiology", description="Heart-related treatments and surgeries.")
    dept2 = Department(name="Neurology", description="Brain and nervous system specialists.")
    db.session.add_all([dept1, dept2])
    db.session.commit()

    #then adding the doctors
    doc1 = User(
        name="Dr. Mehta",
        email="mehta@example.com",
        password="password123",
        contact="9876543210",
        role="Doctor"
    )
    #then the patient

    pat1 = User(
        name="Riya Sharma",
        email="riya@example.com",
        password="password123",
        contact="9123456789",
        role="Patient"
    )

    db.session.add_all([doc1, pat1])
    db.session.commit()
    #connecting doctor and depart

    doctor = Doctor(
        id=doc1.id,
        specialization="Cardiologist",
        departmentid=dept1.id
    )
    db.session.add(doctor)
    db.session.commit()

    #adding patient info
    patient = Patient(
        id=pat1.id,
        dob=date(2000, 5, 17),
        gender='F'
    )
    db.session.add(patient)
    db.session.commit()

    #now the appointment
    appointment = Appointment(
        patientid=patient.id,
        doctorid=doctor.id,
        date=date(2025, 10, 6),
        time=time(10, 30),
        status="Scheduled"
    )
    db.session.add(appointment)
    db.session.commit()

    #treatment
    treatment = Treatment(
        patientid=patient.id,
        doctorid=doctor.id,
        diagnosis="High Blood Pressure",
        procedure="Regular checkup and medication",
        date=date(2025, 10, 6)
    )
    db.session.add(treatment)
    db.session.commit()

    #prescritpion
    prescription = Prescription(
        treatmentid=treatment.id,
        medication="Atenolol 50mg - once daily"
    )
    db.session.add(prescription)
    db.session.commit()

    print("Sample data inserted successfully!")
