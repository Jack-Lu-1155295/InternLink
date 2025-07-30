from functools import wraps
from flask import session, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
from flask import current_app
import re

# handle login and role type
VALID_ROLES = {'student', 'admin', 'employer'}
def login_required(role=None):
    """ Decorator to check if user is logged in and has a specific role.      
        @login_required()             # Any logged in user
        @login_required('student')    # Only logged in students
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # check if logged in. if not redirect to login
            if 'loggedin' not in session:
                return redirect(url_for('login'))
            
            # role must be valid
            user_role = session.get('role')
            if user_role not in VALID_ROLES:
                return render_template('access_denied.html'), 403
            
            # check if role is as expected
            if role and user_role != role:
                return render_template('access_denied.html'), 403
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


# handle file upload
def allowed_file(filename, allowed_exts):
    # Check if a filename has an allowed extension.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts
def handle_file_upload(
    file_storage,       # the uploaded file. e.g., request.file['resume']
    subfolder,          # where under static/ to save the file. e.g., 'resumes'
    username_or_id,     # for file names
    allowed_exts,       # allowed file extensions, e.g., {'pdf'}
    max_size_bytes,     # max size of the file e.g, 5*1024*1024 for 5 MB)
    prefix=None         # if any prefix for filename required. e.g., 'profile_image'
):
    # validate and saves a file upload. returns (relative_path, error_message).  
    # if error_message is None, the upload was successful. 
    if not file_storage or not file_storage.filename:
        return None, "Please choose a file to upload."  
    
    if not allowed_file(file_storage.filename, allowed_exts):
        return None, f"Invalid file type. Allowed types: {', '.join(allowed_exts).upper()}"
    
    # check file size
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)
    if file_size > max_size_bytes:
        return None, f"File exceeds {max_size_bytes // (1024 * 1024)}MB size limit."
    
    # generate filename and path
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    prefix = prefix or subfolder.rstrip('s')   #e.g. resume, logo, profile_image 
    filename = secure_filename(f"{prefix}_{username_or_id}.{ext}")   #filename, e.g., profile_image_someuser.jpeg
    relative_path = os.path.join(subfolder, filename) # 'resumes/resume_someone.pdf'
    abs_path = os.path.join(current_app.root_path, 'static', relative_path) 

    # ensure dict exists
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # save the file
    file_storage.save(abs_path)
    return relative_path.replace('\\', '/'), None


# remove profile image 
def remove_profile_image(
    cursor,                         # MySQL cursor from get_cursor()
    user_id,                        
    user_table='user',
    image_column='profile_image',
    commit_func=None
):
    """
    removes the profile image for a user and delete the file from disk. 
    set profile image path to Null in db.
    returns (success:bool, message:str)
    """
    
    # get the image path
    cursor.execute(f"SELECT {image_column} FROM {user_table} WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    if not row or not row.get(image_column):
        return False, "No profile image to remove."
    
    image_path = row[image_column]
    abs_path = os.path.join(current_app.root_path, 'static', image_path)

    # can't delete default profile image
    if image_path and not image_path.endswith('default_profile.png'):
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception as e:
            return False, f"Failed to delete image: {e}"

    # update database to NULL
    cursor.execute(f"UPDATE {user_table} SET {image_column} = NULL WHERE user_id = %s", (user_id,))
    if commit_func:
        commit_func()        
    return True, "Profile image has been removed. It's now showing default image."

# strong password
def is_strong_password(password):
    # returns None if strong, else an error message
    # At least 8 chars, 1 upper, 1 lower, 1 number, 1 special
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit."
    if not re.search(r'[\W_]', password):  # special char
        return "Password must contain at least one special character (e.g., !@#$%^&*)."
    return None

# valid full name
def is_valid_full_name(full_name):
    #Returns None if valid, else an error message string.
    if not full_name:
        return 'Full name is required.'
    if len(full_name) > 100:
        return 'Your full name cannot exceed 100 characters.'
    if not re.fullmatch(r"[A-Za-z\s'-]+", full_name):
        return "Your full name can only contain letters, spaces, hyphens, and apostrophes."
    return None

# valid email
def is_valid_email(email):
    #Returns None if valid, else an error message string.
    if len(email) > 100:
        return 'Your email address cannot exceed 100 characters.'
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return 'Invalid email address.'
    return None