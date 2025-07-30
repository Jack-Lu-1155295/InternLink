from app import app
from app import db
from flask import redirect, render_template, session, url_for, request, flash
from app.db import get_cursor
import os
from werkzeug.utils import secure_filename
from app.utils import login_required

@app.route('/admin/home')

# only logged in admin can access
@login_required('admin')

def admin_home():
    
     user_id=session['user_id']
     cursor=get_cursor()

     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
     user = cursor.fetchone()

     cursor.close()

     return render_template('admin_home.html', user=user)

Image_Ext = {'png', 'jpg', 'jpeg'}

def allowedfile(filename, allowedext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedext

@app.route('/admin_profile', methods=['GET', 'POST'])
def admin_profile():
    # logged in as admin
    if 'loggedin' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = get_cursor()

    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if request.method == 'POST':
          full_name = request.form.get('full_name')
          email = request.form.get('email')
          profile_image_file = request.files.get('profile_image') or None

          # Update full name in user table
          cursor.execute("UPDATE user SET full_name = %s WHERE user_id = %s", (full_name, user_id))

          # Update email in user table
          cursor.execute("UPDATE user SET email = %s WHERE user_id = %s", (email, user_id))
          
          # Profile Image handling
          if profile_image_file and profile_image_file.filename:
               if allowedfile(profile_image_file.filename, Image_Ext):

                    max_image_size = 1 * 1024 * 1024
                    profile_image_file.seek(0, os.SEEK_END)
                    image_file_size = profile_image_file.tell()
                    profile_image_file.seek(0)

                    if image_file_size > max_image_size:
                         flash("Image cannot exceed 1MB.", "danger")
                         return render_template ('admin_profile.html', user=user)

                    else:
                         ext = profile_image_file.filename.rsplit('.',1)[1].lower()
                         filename = secure_filename(f"image_{user['username']}.{ext}")
                         relative_path = f"profile_images/{filename}"
                         abs_path = os.path.join(app.root_path, 'static', relative_path)
                         profile_image_file.save(abs_path)

                         try:
                              cursor.execute("""
                              UPDATE user SET profile_image = %s WHERE user_id = %s
                              """, (relative_path, user_id))
                              db.get_db().commit()
                              flash('Your profile has been updated successfully.', 'success')
                         
                         except Exception as e:
                              flash('Failed to update profile image.','danger')
                              return render_template('admin_profile.html', user=user)
               else:
                    flash('Only image files (png, jpg, jpeg) are allowed.', 'danger')
                    return render_template ('admin_profile.html', user=user)
  
    # Fetch profile data
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    return render_template('admin_profile.html', user=user)



@app.route('/admin/users', methods=['GET', 'POST'])
def user_management():
     # check logged in user is admin
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role']!='admin':
          return render_template('access_denied.html'), 403
     
     user_id=session['user_id']
     cursor=get_cursor()

     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
     user = cursor.fetchone()

     # Handle POST: status change
     if request.method == 'POST':
          user_id = request.form.get('user_id')
          new_status = request.form.get('new_status')

          if user_id and new_status in ['active', 'inactive']:
              cursor.execute("UPDATE user SET status = %s WHERE user_id = %s", (new_status, user_id))
              db.get_db().commit()

     # Fetch filters from query string (not form)
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
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
        'status': status
      })

