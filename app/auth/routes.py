"""
Authentication routes.
"""
from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, session, flash, current_app
import bcrypt

from . import auth_bp
from ..extensions import get_db
from ..utils.validation import validate_email, validate_password, validate_name


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = validate_name(request.form.get('name'))
            email = validate_email(request.form.get('email'))
            password = validate_password(request.form.get('password'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html')

        db = get_db()
        users_col = db['users']

        # Check if user exists
        if users_col.find_one({'email': email}):
            flash('Email already registered.', 'error')
            return render_template('register.html')

        # Hash password and save
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            'name': name,
            'email': email,
            'password': hashed,
            'role': 'farmer',
            'created_at': datetime.now(timezone.utc),
        }
        users_col.insert_one(user)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = validate_email(request.form.get('email'))
            password = request.form.get('password', '')
        except ValueError:
            flash('Invalid email format.', 'error')
            return render_template('login.html')

        db = get_db()
        users_col = db['users']

        user = users_col.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session.permanent = True  # Enable session expiration
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user.get('role', 'farmer')
            
            current_app.logger.info("User logged in: %s", user['_id'])
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('main.dashboard'))

        current_app.logger.warning("Failed login attempt for email: %s", email)
        flash('Invalid email or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        current_app.logger.info("User logged out: %s", user_id)
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
