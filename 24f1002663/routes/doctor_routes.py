from flask import Blueprint, render_template, session, flash, redirect, url_for

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'doctor':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('doctor_dash.html')
