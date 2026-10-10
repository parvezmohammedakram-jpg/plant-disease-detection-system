"""
Authentication routes.
"""
from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, session, flash, current_app
import bcrypt

from . import auth_bp
from .services import generate_reset_token, verify_reset_token, send_password_reset_email
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


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            email = validate_email(request.form.get('email'))
        except ValueError:
            flash('Invalid email format.', 'error')
            return render_template('forgot_password.html')

        db = get_db()
        user = db['users'].find_one({'email': email})
        
        if user:
            token = generate_reset_token(email)
            send_password_reset_email(email, user['name'], token)
            
        # Always show the same success message to prevent user enumeration
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        try:
            password = validate_password(request.form.get('password'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('reset_password.html', token=token)

        db = get_db()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        db['users'].update_one({'email': email}, {'$set': {'password': hashed}})
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
