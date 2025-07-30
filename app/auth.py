from app import app
from app import db
from flask import redirect, render_template, request, session, url_for, flash
from flask_bcrypt import Bcrypt
from app.utils import handle_file_upload, is_strong_password, is_valid_email, is_valid_full_name
from app.config import UPLOAD_CONFIG
import re
import os

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role assigned to new users upon registration.
DEFAULT_USER_ROLE = 'student'

def user_home_url():
    if 'loggedin' in session:
        role = session.get('role', None)

        if role=='student':
            home_endpoint='student_home'
        elif role=='employer':
            home_endpoint='employer_home'
        elif role=='admin':
            home_endpoint='admin_home'
        else:
            home_endpoint = 'logout'
    else:
        home_endpoint = 'login'
    
    return url_for(home_endpoint)

@app.route('/')
def root():

    return redirect(user_home_url())

@app.route('/login', methods=['GET', 'POST'])
def login():

    if 'loggedin' in session:
         return redirect(user_home_url())

    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        # Get the login details submitted by the user.
        username = request.form['username']
        password = request.form['password']

        # Attempt to validate the login details against the database.
        with db.get_cursor() as cursor:

            cursor.execute('''
                           SELECT user_id, username, password_hash, role, status
                           FROM user
                           WHERE username = %s;
                           ''', (username,))
            account = cursor.fetchone()
            
            if account is not None:
                password_hash = account['password_hash']
                
                if flask_bcrypt.check_password_hash(password_hash, password):

                    if account['status'] == 'inactive':
                        flash('Your account is deactivated. Please contact the administrator.', 'danger')
                        return redirect(user_home_url())
                    
                    session['loggedin'] = True
                    session['user_id'] = account['user_id']
                    session['username'] = account['username']
                    session['role'] = account['role']

                    return redirect(user_home_url())
                else:

                    return render_template('login.html',
                                           username=username,
                                           password_invalid=True)
            else:
                return render_template('login.html', 
                                       username=username,
                                       username_invalid=True)

    return render_template('login.html')

# signup
@app.route('/signup', methods=['GET','POST'])
def signup():

    if 'loggedin' in session:
         return redirect(user_home_url())
    
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'full_name' in request.form:
        # Get the details submitted via the form on the signup page, and store
        # the values in temporary local variables for ease of access.
        # Mandotary fields:
        username = request.form.get('username', '')
        full_name = request.form.get('full_name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        # Optional fields:
        university = request.form.get('university', '').strip() or None
        course = request.form.get('course', '').strip() or None
        
        resume_file = request.files.get('resume') or None
        profile_image_file = request.files.get('profile_image') or None

        # We start by assuming that everything is okay. If we encounter any
        # errors during validation, we'll store an error message in one or more
        # of these variables so we can pass them through to the template.
        username_error = None
        full_name_error = None
        email_error = None
        password_error = None
        resume_error = None
        profile_image_error = None
        confirm_password_error = None

        # Check whether there's an account with this username in the database.
        with db.get_cursor() as cursor:
            cursor.execute('SELECT user_id FROM user WHERE username = %s;',
                           (username,))
            account_already_exists = cursor.fetchone() is not None
        
        # Validate the username, ensuring that it's unique (as we just checked
        # above) and meets the naming constraints of our web app.
        if account_already_exists:
            username_error = 'An account already exists with this username.'
        elif len(username) > 50:
            # The user should never see this error during normal conditions,
            # because we set a maximum length of 50 on the input field in the
            # template. However, a user or attacker could easily override that
            # and submit a longer value, so we need to handle that case.
            username_error = 'Your username cannot exceed 50 characters.'
        elif not re.match(r'(?!.*\s)[A-Za-z0-9.]+', username):
            username_error = 'Your username can only contain letters, numbers, and periods (no spaces).'            

        # Validate the new user's full name and email address (via utils.py)
        full_name_error = is_valid_full_name(full_name)
        email_error = is_valid_email(email)
        
        # password strength validation via utils.py
        password_strength_msg = is_strong_password(password)
        if password_strength_msg:
            password_error = password_strength_msg
        elif password != confirm_password:
            confirm_password_error = 'Passwords do not match'        

        # Resume handling
        resume_relative_path = None
        if resume_file and resume_file.filename:
            cfg_resume = UPLOAD_CONFIG['resume']
            resume_relative_path, resume_err = handle_file_upload(
                resume_file, 
                subfolder=cfg_resume['subfolder'],
                username_or_id=username,
                allowed_exts=cfg_resume['allowed_exts'],
                max_size_bytes=cfg_resume['max_size'],
                prefix=cfg_resume['prefix']
            )
            if resume_err:
                resume_error = resume_err
       
        # Profile Image handling
        pfimage_relative_path = None
        if profile_image_file and profile_image_file.filename:
            cfg_img = UPLOAD_CONFIG['profile_image']
            pfimage_relative_path, img_err=handle_file_upload(
                profile_image_file,
                subfolder=cfg_img['subfolder'],
                username_or_id=username,
                allowed_exts=cfg_img['allowed_exts'],
                max_size_bytes=cfg_img['max_size'],
                prefix=cfg_img['prefix']
            )
            if img_err:
                profile_image_error = img_err

        if (username_error or email_error or password_error or confirm_password_error or full_name_error or resume_error or profile_image_error):
            # One or more errors were encountered, so send the user back to the
            # signup page with their username and email address pre-populated.
            # For security reasons, we never send back the password they chose.
            return render_template('signup.html',
                                   username=username,
                                   email=email,
                                   full_name=full_name,
                                   university=university,
                                   course=course,
                                   username_error=username_error,
                                   email_error=email_error,
                                   password_error=password_error,
                                   full_name_error=full_name_error,
                                   resume_error=resume_error,
                                   profile_image_error=profile_image_error,
                                   confirm_password_error=confirm_password_error)
        
            # The new account details are valid. Hash the user's new password
            # and create their account in the database.
        password_hash = flask_bcrypt.generate_password_hash(password)
            
            # Note: In this example, we just assume the SQL INSERT statement
            # below will run successfully. But what if it doesn't?
            #
            # If the INSERT fails for any reason, MySQL Connector will throw an
            # exception and the user will receive a generic error page. We
            # should implement our own error handling here to deal with that
            # possibility, and display a more useful message to the user.
        try:
            with db.get_cursor() as cursor:
            
            # Insert into user table
                cursor.execute('''
                    INSERT INTO user (username, full_name, email, password_hash, profile_image)
                    VALUES (%s, %s, %s, %s, %s);
                ''', (username, full_name, email, password_hash, pfimage_relative_path))
            
            # Insert into student table
                user_id = cursor.lastrowid
                cursor.execute('''
                    INSERT INTO student (user_id, university, course, resume_path)
                    VALUES (%s, %s, %s, %s);
                ''', (user_id, university, course, resume_relative_path))

        except Exception:
            return render_template('signup.html', error="Database error, failed to create account.")

        return render_template('signup.html', signup_successful=True)            

    # This was a GET request, or an invalid POST (no username, email, and/or
    # password). Render the signup page with no pre-populated form fields or
    # error messages.
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
    # Note that nothing actually happens on the server when a user logs out: we
    # just remove the cookie from their web browser. They could technically log
    # back in by manually restoring the cookie we've just deleted. In a high-
    # security web app, you may need additional protections against this (e.g.
    # keeping a record of active sessions on the server side).
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    
    return redirect(url_for('login'))