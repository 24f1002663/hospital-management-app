from flask import Flask, render_template
from model import db, User, Department, Doctor, Patient, Prescription, Appointment, Treatment
from routes.authentication import auth_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp
from routes.patient_routes import patient_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "my-secret-key"

    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

    @app.route('/')
    def index():
        return render_template("home.html")

    return app

def create_admin():
    admin=User.query.filter_by(role='admin').first()
    if not admin:
        admin=  User(
            name='admin',
            email='admin@hospital.com',
            password='admin123',
            contact='1233445566',
            role='admin'

        )
        db.session.add(admin)
        db.session.commit()
        print("default admin created")

    else:
        print("admin exists")
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all() 
        create_admin()
    app.run(debug=True, port=5000)



