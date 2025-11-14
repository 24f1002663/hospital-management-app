from flask import Flask, render_template
#importing tables form the model
from model import db, User, Department, Doctor, Patient, Prescription, Appointment, Treatment
#as it is not feasible to write all the routes in one file we breakdown and use blueprints that defines module like a mini app. 
from routes.authentication import auth_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp
from routes.patient_routes import patient_bp
from flask_mail import Mail,Message
from werkzeug.security import generate_password_hash

mail=Mail()

def create_app():
    app = Flask(__name__)
    # connecting to database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    # we keep track modifications false because we don’t need to track every object change in memory.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #to protect attacks
    app.secret_key = "my-secret-key"
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT']=587
    app.config['MAIL_USE_TLS']=True
    app.config['MAIL_USERNAME']="24f1002663@ds.study.iitm.ac.in"
    app.config['MAIL_PASSWORD']="jmsd zdxx mphx ogyk"
    #this binds my db to the app
    # and now we fix the routes so they dont overlap
    db.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

    @app.route('/')
    # to render the home page
    def index():
        return render_template("home.html")

    return app

def create_admin():
    admin=User.query.filter_by(role='admin').first()
    # here we can making a default admin that will be created when app.py will run
    if not admin:
        admin=  User(
            name='admin',
            email='admin@hospital.com',
            password=generate_password_hash('admin123'),
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
    # everytime the app is run the tables are created first time
    with app.app_context():
        db.create_all() 
        create_admin()
    app.run(debug=True, port=5000)



