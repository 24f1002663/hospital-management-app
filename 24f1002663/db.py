from app import app, db
from model import User,Department,Doctor,Treatment,Patient,Prescription,Appointment
with app.app_context():
    db.create_all()
    print(" Database created successfully!")