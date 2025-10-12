from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from datetime import date, time
# User Table
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
    doctor=db.relationship("Doctor", backref= "user",uselist= False)
    patient=db.relationship("Patient", backref= "user",uselist=False)
# Doctor Table
class Doctor(db.Model):
    __tablename__ = "doctor"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    departmentid = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    treatments = db.relationship('Treatment', backref='doctor', lazy=True)
# Patient Table
class Patient(db.Model):
    __tablename__ = "patient"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('M', 'F', name='gender_enum'), nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    treatments = db.relationship('Treatment', backref='patient', lazy=True)
# Department
class Department(db.Model):
    __tablename__ = "department"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    doctors = db.relationship('Doctor', backref='department', lazy=True)
# Appointment Table
class Appointment(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    patientid = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    doctorid = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False)
# Treatment Table
class Treatment(db.Model):
    __tablename__ = "treatment"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    patientid = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    doctorid = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)
    diagnosis = db.Column(db.String(255), nullable=False)
    procedure = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    prescriptions = db.relationship('Prescription', backref='treatment', lazy=True)
# Prescription Table
class Prescription(db.Model):
    __tablename__ = "prescription"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    treatmentid = db.Column(db.Integer, db.ForeignKey('treatment.id'), nullable=True)
    medication = db.Column(db.String(255), nullable=False)
