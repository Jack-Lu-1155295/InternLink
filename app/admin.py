"""
admin.py

Routes for admin features: 
- Admin home page
- Admin profile - view and update info
- User management - view a list of all users, filtering and change account status
- View user profile - under user management, admin can choose to view each user's profile
"""


from app import app
from app import db
from flask import redirect, render_template, session, url_for, request, flash
from app.db import get_cursor
import os
from werkzeug.utils import secure_filename
from app.utils import login_required, handle_file_upload, is_valid_full_name, is_valid_email, remove_profile_image
from app.config import UPLOAD_CONFIG

# Get user information from the db by user id. This returns user info as a dict or None if not found.
def get_user(cursor, user_id):
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

@app.route('/admin/home')
# only logged in admin can access
@login_required('admin')
def admin_home():

     user_id=session['user_id']
     cursor=get_cursor()

     user = get_user(cursor, user_id)
     cursor.close()

     return render_template('admin_home.html', user=user)


@app.route('/admin_profile', methods=['GET', 'POST'])
@login_required('admin') # only logged in admin can access
def admin_profile():
     # this is to view and edit the admin user's own profile. 
     # admin user can edit their full name, email, uploading/removing profile image.
     user_id = session['user_id']
     cursor = get_cursor()
     user = get_user(cursor, user_id)

     full_name_error = None
     email_error = None

     if request.method == 'POST':
          form_type = request.form.get("form_type")

          if form_type == 'profile_info':
               full_name = request.form.get('full_name', '').strip()
               email = request.form.get('email', '').strip()
               # validation of email and full name
               full_name_error = is_valid_full_name(full_name)
               email_error = is_valid_email(email)
               if full_name_error or email_error:
                    cursor.close()
                    return render_template('admin_profile.html', user=user, full_name_error=full_name_error, email_error=email_error)
               cursor.execute("UPDATE user SET full_name = %s, email = %s WHERE user_id = %s", (full_name, email, user_id))
               db.get_db().commit()
               flash('Profile info updated successfully.', 'success')

          # Profile Image handling
          elif form_type == "profile_image":
               profile_image_file = request.files.get('profile_image') #get file
               cfg_img = UPLOAD_CONFIG['profile_image']  # get file setting
               # call handler
               profile_image_path, img_error = handle_file_upload(
                    profile_image_file,
                    subfolder=cfg_img["subfolder"],
                    username_or_id=user["username"],     
                    allowed_exts=cfg_img["allowed_exts"],
                    max_size_bytes=cfg_img["max_size"],
                    prefix=cfg_img["prefix"])
               # error message
               if img_error:
                    flash (img_error, 'danger')
                    return render_template ('admin_profile.html', user=user)
               # save path to db
               elif profile_image_path:
                    cursor.execute("UPDATE user SET profile_image = %s WHERE user_id = %s", (profile_image_path, user_id))
                    db.get_db().commit()
                    flash('Profile image updated successfully.', 'success')
                    user = get_user(cursor, user_id)
                    cursor.close()
                    return render_template('admin_profile.html', user=user)
          
          # remove profile image
          elif form_type == "remove_profile_image":
               success, msg = remove_profile_image(
               cursor,
               user_id,
               user_table='user',
               image_column='profile_image',
               commit_func=lambda: db.get_db().commit()
               )
               if not success:
                    flash(msg, 'danger')
                    return render_template ('admin_profile.html', user=user)
               else:
                    flash(msg, "success")
                    user = get_user(cursor, user_id)
                    cursor.close()
                    return render_template ('admin_profile.html', user=user)
 
     # Fetch profile data
     user = get_user(cursor, user_id)
     cursor.close()

     return render_template('admin_profile.html', user=user)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required('admin') # only logged in admin can access
def user_management():
     # a list of all users for admin to manage user status. 
     user_id=session['user_id']
     cursor=get_cursor()
     user = get_user(cursor, user_id)

     # Handle POST: status change
     if request.method == 'POST':
          user_id = request.form.get('user_id')
          new_status = request.form.get('new_status')

          if user_id and new_status in ['active', 'inactive']:
              cursor.execute("UPDATE user SET status = %s WHERE user_id = %s", (new_status, user_id))
              db.get_db().commit()

     # Fetch filters from query string (not form)
     username = request.args.get('username', '').strip()
     first_name = request.args.get('first_name', '').strip()
     last_name = request.args.get('last_name', '').strip()
     role = request.args.get('role', '').strip()
     status = request.args.get('status', '').strip()

     query = """
        SELECT user_id, username, full_name, email, role, status 
        FROM user 
        WHERE 1=1
     """
     params = []

     if username:
          query += " AND username LIKE %s"
          params.append(f"{username}%")
     if first_name:
          query += " AND full_name LIKE %s"
          params.append(f"{first_name}%")
     if last_name:
          query += " AND full_name LIKE %s"
          params.append(f"% {last_name}%")
     if role:
          query += " AND role = %s"
          params.append(role)
     if status:
          query += " AND status = %s"
          params.append(status)

     cursor.execute(query, tuple(params))
     users = cursor.fetchall()
     cursor.close()

     return render_template('admin_users.html', user=user, users=users, filters={
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
        'status': status
      })

@app.route('/admin/user/<int:user_id>')
@login_required('admin') # only logged in admin can access
def admin_view_user_profile(user_id):
     # for admin user to view A user's profile.
     cursor = get_cursor()
     user = get_user(cursor, session['user_id']) # admin

     user_profile = get_user(cursor, user_id) # user to be viewed
     student_info = None
     employer_info = None

     # if it's student, show student info
     if user_profile['role'] == 'student':
          cursor.execute("SELECT university, course, resume_path FROM student WHERE user_id = %s", (user_id,))
          student_info = cursor.fetchone()

     # if it's employer, show employer info
     elif user_profile['role'] == 'employer':
          cursor.execute("SELECT company_name, company_description, website, logo_path FROM employer WHERE user_id = %s", (user_id,))
          employer_info = cursor.fetchone()
        
     cursor.close()
     return render_template(
          'admin_view_user_profile.html',
          user=user,
          user_profile=user_profile,
          student_info=student_info,
          employer_info=employer_info
     )