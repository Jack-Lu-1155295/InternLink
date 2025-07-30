from app import app
from app import db
from flask import redirect, render_template, session, url_for, request, flash
from app.db import get_cursor
import os
from werkzeug.utils import secure_filename
from app.utils import login_required, handle_file_upload, remove_profile_image
from app.config import UPLOAD_CONFIG

# get user id and employer info
def get_employer_user_and_profile(cursor, user_id):
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM employer WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()
    return user, profile

@app.route('/employer/home')
# only logged in employer can access
@login_required('employer')
def employer_home():
     
     user_id = session['user_id']
     cursor = get_cursor()
     user, profile = get_employer_user_and_profile(cursor, user_id)
     cursor.close()
     return render_template('employer_home.html', user=user, profile=profile)


@app.route('/employer_profile', methods=['GET', 'POST'])
@login_required('employer') # only logged in employer has access
def employer_profile():
     #Get user information
     user_id = session['user_id']
     cursor = get_cursor()
     user, profile = get_employer_user_and_profile(cursor, user_id)

     if request.method == 'POST':
          form_type = request.form.get("form_type")

          # update profile info
          if form_type == 'profile_info':
               full_name = request.form.get('full_name')
               company_name = request.form.get('company_name')
               company_description = request.form.get('company_description')
               website = request.form.get('website')

               cursor.execute("UPDATE user SET full_name = %s WHERE user_id = %s", (full_name, user_id))
               cursor.execute("""
                    UPDATE employer SET company_name = %s, company_description = %s, website = %s 
                    WHERE user_id = %s
               """, (company_name, company_description, website, user_id))
               db.get_db().commit()
               flash('Profile info updated successfully.', 'success')
          
          # Profile Image handling
          elif form_type == "profile_image":
               profile_image_file = request.files.get('profile_image')
               cfg_img = UPLOAD_CONFIG['profile_image']
               profile_image_path, img_error = handle_file_upload(
                    profile_image_file,          
                    subfolder=cfg_img["subfolder"],
                    username_or_id=user["username"],
                    allowed_exts=cfg_img["allowed_exts"],
                    max_size_bytes=cfg_img["max_size"],
                    prefix=cfg_img["prefix"])
               if img_error:
                    flash(img_error, "danger")
                    return render_template('employer_profile.html', user=user, profile=profile)
               elif profile_image_path:
                    cursor.execute("UPDATE user SET profile_image = %s WHERE user_id = %s", (profile_image_path, user_id))
                    db.get_db().commit()
                    flash('Profile image updated successfully.', 'success')
                    # Refresh user/profile for instant update
                    user, profile = get_employer_user_and_profile(cursor, user_id)
                    cursor.close()
                    return render_template('employer_profile.html', user=user, profile=profile)

          # Profile image removal (back to default)
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
                    return render_template('employer_profile.html', user=user, profile=profile)
               else:
                    flash(msg, 'success')
                    user, profile = get_employer_user_and_profile(cursor, user_id)
                    cursor.close()
                    return render_template('employer_profile.html', user=user, profile=profile)                    

          # Logo upload
          elif form_type == "company_logo":
               logo_file = request.files.get('logo')
               logo_path = None
               cfg_logo = UPLOAD_CONFIG['logo']
               logo_path, logo_error = handle_file_upload(
                    logo_file,
                    subfolder=cfg_logo["subfolder"],
                    username_or_id=user_id,  
                    allowed_exts=cfg_logo["allowed_exts"],
                    max_size_bytes=cfg_logo["max_size"],
                    prefix=cfg_logo["prefix"]
               )
               if logo_error:
                    flash(logo_error, "danger")
                    return render_template('employer_profile.html', user=user, profile=profile)
               elif logo_path:
                    cursor.execute("UPDATE employer SET logo_path = %s WHERE user_id = %s", (logo_path, user_id))
                    db.get_db().commit()
                    flash('Company logo updated successfully.', 'success')
                    user, profile = get_employer_user_and_profile(cursor, user_id)
                    cursor.close()
                    return render_template('employer_profile.html', user=user, profile=profile)
    
    # Fetch profile data
     user, profile = get_employer_user_and_profile(cursor, user_id)
     cursor.close()

     return render_template('employer_profile.html', user=user, profile=profile)
