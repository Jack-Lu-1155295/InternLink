from app import app
from app import db
from flask import redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
import re
import os
from werkzeug.utils import secure_filename

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role assigned to new users upon registration.
DEFAULT_USER_ROLE = 'student'

def user_home_url():
    """Generates a URL to the homepage for the currently logged-in user.
    
    If the user is not logged in, this returns the URL for the login page
    instead. If the user appears to be logged in, but the role stored in their
    session cookie is invalid (i.e. not a recognised role), it returns the URL
    for the logout page to clear that invalid session data."""
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
    """Root endpoint (/)
    
    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    return redirect(user_home_url())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page endpoint.

    Methods:
    - get: Renders the login page.
    - post: Attempts to log the user in using the credentials supplied via the
        login form, and either:
        - Redirects the user to their role-specific homepage (if successful)
        - Renders the login page again with an error message (if unsuccessful).
    
    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())

    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        # Get the login details submitted by the user.
        username = request.form['username']
        password = request.form['password']

        # Attempt to validate the login details against the database.
        with db.get_cursor() as cursor:
            # Try to retrieve the account details for the specified username.
            #
            # Note: we use a Python multiline string (triple quote) here to
            # make the query more readable in source code. This is just a style
            # choice: the line breaks are ignored by MySQL, and it would be
            # equally valid to put the whole SQL statement on one line like we
            # do at the beginning of the `signup` function.
            cursor.execute('''
                           SELECT user_id, username, password_hash, role
                           FROM user
                           WHERE username = %s;
                           ''', (username,))
            account = cursor.fetchone()
            
            if account is not None:
                # We found a matching account: now we need to check whether the
                # password they supplied matches the hash in our database.
                password_hash = account['password_hash']
                
                if flask_bcrypt.check_password_hash(password_hash, password):
                    # Password is correct. Save the user's ID, username, and role
                    # as session data, which we can access from other routes to
                    # determine who's currently logged in.
                    # 
                    # Users can potentially see and edit these details using their
                    # web browser. However, the session cookie is signed with our
                    # app's secret key. That means if they try to edit the cookie
                    # to impersonate another user, the signature will no longer
                    # match and Flask will know the session data is invalid.
                    session['loggedin'] = True
                    session['user_id'] = account['user_id']
                    session['username'] = account['username']
                    session['role'] = account['role']

                    return redirect(user_home_url())
                else:
                    # Password is incorrect. Re-display the login form, keeping
                    # the username provided by the user so they don't need to
                    # re-enter it. We also set a `password_invalid` flag that
                    # the template uses to display a validation message.
                    return render_template('login.html',
                                           username=username,
                                           password_invalid=True)
            else:
                # We didn't find an account in the database with this username.
                # Re-display the login form, keeping the username so the user
                # can see what they entered (otherwise, they might just keep
                # trying the same thing). We also set a `username_invalid` flag
                # that tells the template to display an appropriate message.
                #
                # Note: In this example app, we tell the user if the user
                # account doesn't exist. Many websites (e.g. Google, Microsoft)
                # do this, but other sites display a single "Invalid username
                # or password" message to prevent an attacker from determining
                # whether a username exists or not. Here, we accept that risk
                # to provide more useful feedback to the user.
                return render_template('login.html', 
                                       username=username,
                                       username_invalid=True)

    # This was a GET request, or an invalid POST (no username and/or password),
    # so we just render the login form with no pre-populated details or flags.
    return render_template('login.html')


# Define allowed type of files
Resume_Ext = {'pdf'}
Image_Ext = {'png', 'jpg', 'jpeg'}

def allowedfile(filename, allowedext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedext

@app.route('/signup', methods=['GET','POST'])

def signup():
    """Signup (registration) page endpoint.

    Methods:
    - get: Renders the signup page.
    - post: Attempts to create a new user account using the details supplied
        via the signup form, then renders the signup page again with a welcome
        message (if successful) or one or more error message(s) explaining why
        signup could not be completed.

    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
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
        # Optional fields:
        university = request.form.get('university', '').strip() or None
        course = request.form.get('course', '').strip() or None
        
        resume_file = request.files.get('resume') or None
        profile_image_file = request.files.get('profile_image') or None

        resume_path = None
        profile_image = None
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

        # Validate the new user's full name. 
        if len(full_name) == 0:
            full_name_error = 'Full name is required.'
        elif len(full_name) > 100:
            full_name_error = 'Your full name cannot exceed 100 characters.'
        elif not re.fullmatch(r"[A-Za-z\s'-]+", full_name):
            full_name_error = 'Your full name can only contain letters, spaces, hyphens, and apostrophes.'

        # Validate the new user's email address. Note: The regular expression
        # we use here isn't a perfect check for a valid address, but is
        # sufficient for this example.
        if len(email) > 100:
            # As above, the user should never see this error under normal
            # conditions because we set a maximum input length in the template.
            email_error = 'Your email address cannot exceed 100 characters.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            email_error = 'Invalid email address.'
                
        # Validate password. Think about what other constraints might be useful
        # here for security (e.g. requiring a certain mix of character types,
        # or avoiding overly-common passwords). Make sure that you clearly
        # communicate any rules to the user, either through hints on the signup
        # page or with clear error messages here.
        #
        # Note: Unlike the username and email address, we don't enforce a
        # maximum password length. Because we'll be storing a hash of the
        # password in our database, and not the password itself, it doesn't
        # matter how long a password the user chooses. Whether it's 8 or 800
        # characters, the hash will always be the same length.
        confirm_password=request.form.get('confirm_password','')
        if len(password) < 8:
            password_error = 'Please choose a longer password!'
        elif password != confirm_password:
            confirm_password_error = 'Passwords do not match'        

        # Resume Validation
        if resume_file and resume_file.filename:
            if allowedfile(resume_file.filename, Resume_Ext):

                max_resume_size = 5 * 1024 * 1024
                resume_file.seek(0, os.SEEK_END)
                resume_file_size = resume_file.tell()
                resume_file.seek(0)
                
                if resume_file_size > max_resume_size:
                    resume_error = "Resume file cannot exceed 5MB."
                
                else:
                    ext = resume_file.filename.rsplit('.',1)[1].lower()
                    filename = secure_filename(f"resume_{username}.{ext}")
                    resume_path = os.path.join('static', 'resumes', filename).replace('\\', '/')
                    resume_file.save(resume_path)
            else:
                resume_error = 'You can only upload your resume in PDF format.' 

        # Profile Image validation
        if profile_image_file and profile_image_file.filename:
            if allowedfile(profile_image_file.filename, Image_Ext):

                max_image_size = 1 * 1024 * 1024
                profile_image_file.seek(0, os.SEEK_END)
                image_file_size = profile_image_file.tell()
                profile_image_file.seek(0)

                if image_file_size > max_image_size:
                    profile_image_error = "Image cannot exceed 1MB."

                else:
                    ext = profile_image_file.filename.rsplit('.',1)[1].lower()
                    filename = secure_filename(f"image_{username}.{ext}")
                    profile_image = os.path.join('static','profile_images', filename).replace('\\', '/')
                    profile_image_file.save(profile_image)
            else:
                profile_image_error = 'Only image files (png, jpg, jpeg, gif) are allowed.'


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
                ''', (username, full_name, email, password_hash, profile_image))
            
            # Insert into student table
                user_id = cursor.lastrowid
                cursor.execute('''
                    INSERT INTO student (user_id, university, course, resume_path)
                    VALUES (%s, %s, %s, %s);
                ''', (user_id, university, course, resume_path))

        except Exception:
            return render_template('signup.html', error="Database error, failed to create account.")

        return render_template('signup.html', signup_successful=True)            

    # This was a GET request, or an invalid POST (no username, email, and/or
    # password). Render the signup page with no pre-populated form fields or
    # error messages.
    return render_template('signup.html')




@app.route('/profile')
def profile():
    """User Profile page endpoint.

    Methods:
    - get: Renders the user profile page for the current user.

    If the user is not logged in, requests will redirect to the login page.
    """
    if 'loggedin' not in session:
         return redirect(url_for('login'))

    # Retrieve user profile from the database.
    with db.get_cursor() as cursor:
        cursor.execute('SELECT username, email, role FROM users WHERE user_id = %s;',
                       (session['user_id'],))
        profile = cursor.fetchone()

    return render_template('profile.html', profile=profile)

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