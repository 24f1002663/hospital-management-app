# Hospital Management System (HMS)

## Overview

This is a web-based Hospital Management System built using **Flask** and **SQLite**.  
It supports three roles:

- **Admin** – manages doctors, patients, and appointments  
- **Doctor** – manages appointments, treatments, and availability  
- **Patient** – registers, books appointments, views history, and edits profile  

The app uses:

- **Flask** for backend routing and logic  
- **SQLAlchemy** as ORM  
- **SQLite** as the database  
- **HTML + CSS + Jinja** for templates and UI  

## Features
### Admin
- Login as admin (predefined)
- View total number of doctors, patients, and appointments
- Register new doctors
- View and search doctors by name/specialization
- View and search patients by name / ID / contact
- Blacklist / Unblacklist doctors and patients
- View all appointments
- Create, edit, and delete appointments
- Prevents:
  - booking a doctor on a day they are unavailable  
  - double booking at the same time slot

### Doctor

- Login using doctor credentials
- View upcoming appointments (next 7 days)
- View past appointments (Completed / Cancelled)
- Mark appointments as **Completed** or **Cancelled**
- Enter diagnosis, procedure, and prescriptions for each appointment
- View full medical history of a patient
- Set / update their availability for the next 7 days
- View and edit their own profile

### Patient

- Register and login as patient
- View and edit profile (name, email, contact, DOB, gender, password)
- Search doctors by name / specialization
- View a doctor’s availability (next 7 days) before booking
- Book appointments only:
  - if doctor is available that day  
  - if chosen time slot is free  
- View upcoming appointments with status
- View past appointments and treatment details
- Cancel own appointments


project_root/
│
├── app.py                   # Flask application factory and app entry point
├── model.py                 # Database models (User, Doctor, Patient, Appointment, etc.)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── api.yaml                 # Simple API definition (for submission)
│
├── routes/
│   ├── authentication.py    # Login, register, logout routes
│   ├── admin_routes.py      # Admin dashboard and management routes
│   ├── doctor_routes.py     # Doctor dashboard and treatment routes
│   └── patient_routes.py    # Patient dashboard and booking routes
│
└──templates/
├── admin_dash.html
├── doctor_availability.html
├── doctor_dash.html
├── doctor_past_appointments.html
├── doctor_profile.html
├── doctor_self_profile.html
├── doctor_treatment.html
├── home.html
├── login.html
├── manage_appointments.html
├── patient_book_appointment.html
├── patient_dash.html
├── patient_history.html
├── patient_history_single.html
├── patient_profile.html
├── patient_view_doctors.html
├── register.html
├── register_doctor.html
├── view_doctors.html
└── view_patients.html
Step-by-Step Installation
1. Clone the Repository
git clone https://github.com/24f1002663/Hospital-Management-App.git  
cd Hospital-Management-App 
2. Create Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Initialize the Database
python create_db.py


This will automatically:
Create the SQLite database
Generate all required tables (Doctors, Patients, Appointments, Treatments, etc.)
Insert the default admin account

5. Run the Application
python app.py

6. Access the Web App

Open your browser

Go to: http://localhost:5000

Your medical appointment system is now running! 🎉

##Default Login Credentials
Admin Login
Email: admin@hospital.com
Password: admin123