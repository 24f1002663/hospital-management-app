from flask import Blueprint, render_template, session, flash, redirect, url_for

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('admin_dash.html')
