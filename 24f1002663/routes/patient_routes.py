from flask import Blueprint, render_template, session, flash, redirect, url_for

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'patient':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('patient_dash.html')
