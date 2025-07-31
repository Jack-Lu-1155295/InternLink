"""
student.py

Routes for student features: 
- Student home page
- Internship application
- Student profile - view and update profile info
"""


from app import app
from app import db
from flask import redirect, render_template, session, url_for
from flask import request, flash
from app.db import get_cursor
from werkzeug.utils import secure_filename
import os
from app.utils import login_required, handle_file_upload, remove_profile_image
from app.config import UPLOAD_CONFIG

# get user id and student info
def get_student_user_and_profile(cursor, user_id):
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.execute("""
        SELECT u.full_name, u.email, u.profile_image, s.university, s.course, s.resume_path
        FROM user u
        JOIN student s ON u.user_id = s.user_id
        WHERE u.user_id = %s
    """, (user_id,))
    profile = cursor.fetchone()
    return user, profile

@app.route('/student/home')
# only logged in student can access
@login_required('student')
def student_home():
   
     user_id=session['user_id']
     cursor=get_cursor()

     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
     user = cursor.fetchone()

     cursor.close()
     # The user is logged in with a student account, so render the student
     # homepage as requested.
     return render_template('student_home.html', user=user)


@app.route('/student/apply/<int:internship_id>', methods=['GET', 'POST'])
@login_required('student') # only logged in student can access
def apply_internship(internship_id):

     user_id=session['user_id']
     cursor=get_cursor()
     cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
     user = cursor.fetchone()

     # Get student_id using user_id
     cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
     result = cursor.fetchone()
     if not result:
          return render_template('access_denied.html'), 403
     student_id = result['student_id']
     
     # Internship details
     cursor.execute("""
          SELECT i.*, e.company_name
          FROM internship i
          JOIN employer e ON i.company_id = e.emp_id
          WHERE i.internship_id = %s
          """,(internship_id,)) 
     internship = cursor.fetchone()

     # Student details
     cursor.execute("""
          SELECT u.full_name, u.email, s.university, s.course, s.resume_path
          FROM user u
          JOIN student s ON u.user_id = s.user_id
          WHERE u.user_id = %s
          """,(user_id,)) 
     student_info = cursor.fetchone()


     # Check if the student has applied this internship already
     cursor.execute("""
          SELECT * FROM application
          WHERE student_id = %s AND internship_id = %s
          """, (student_id, internship_id))
     already_applied = cursor.fetchone() is not None

     # If already applied, display a message and do NOT show form
     if already_applied:
          cursor.close()
          return render_template('apply_internship.html', user=user, internship=internship, student_id=student_id, student_info=student_info, already_applied=True)
     
     # Application
     if request.method == 'POST':
          cover_letter = request.form.get('cover_letter', '') or None
          resume_file = request.files.get('resume') or None
          current_resume_path = student_info['resume_path']
          # Handle resume upload 
          if resume_file and resume_file.filename:
               cfg_resume = UPLOAD_CONFIG['resume']
               resume_path, resume_error = handle_file_upload(
                    resume_file,
                    subfolder=cfg_resume["subfolder"],
                    username_or_id=user["username"],
                    allowed_exts=cfg_resume["allowed_exts"],
                    max_size_bytes=cfg_resume["max_size"],
                    prefix=cfg_resume["prefix"]
               )
               # error message
               if resume_error:
                    flash(resume_error, "danger")
                    return render_template('apply_internship.html', user=user, internship=internship, student_id=student_id, student_info=student_info)
               # update db
               if resume_path:
                    cursor.execute("UPDATE student SET resume_path = %s WHERE user_id = %s", (resume_path, user_id))
               
               else:
                    flash('You need a valid resume to apply. Only PDF allowed.', 'danger')
                    return render_template('apply_internship.html', user=user, internship=internship, student_id=student_id, student_info=student_info)
          
          # make sure user can appy without upload a new resume
          elif current_resume_path:
               resume_path = current_resume_path

          else:
               # No file uploaded and no resume exists
               flash('You must upload a resume before applying.', 'danger')
               return render_template('apply_internship.html', user=user, internship=internship, student_id=student_id, student_info=student_info)

     # Insert application into database
          try:
               cursor.execute("""
               INSERT INTO application (internship_id, student_id, cover_letter)
               VALUES (%s, %s, %s)
          """, (internship_id, student_id, cover_letter))
               db.get_db().commit()

          except Exception as e:
               print("Application insert error:", e)
               flash('Failed to submit application. Please try again.', 'danger')
               return render_template('apply_internship.html', user=user, internship=internship, student_id=student_id, student_info=student_info)

          cursor.close()
          flash('Application submitted successfully!', 'success')
          return redirect(url_for('student_home'))
     
     return render_template('apply_internship.html', user=user, internship=internship, student_id=student_id, student_info=student_info)

@app.route('/student_profile', methods=['GET', 'POST'])
@login_required('student')  # only logged student can access
def student_profile():
     # get user information and student information
     user_id = session['user_id']
     cursor = get_cursor()
     user, profile = get_student_user_and_profile(cursor, user_id)

     if request.method == 'POST':
          form_type = request.form.get("form_type")
        
          # Update full name, university, course
          if form_type == "profile_info":
               full_name = request.form.get('full_name')
               university = request.form.get('university')
               course = request.form.get('course')
               cursor.execute("UPDATE user SET full_name = %s WHERE user_id = %s", (full_name, user_id))
               cursor.execute("UPDATE student SET university = %s, course = %s WHERE user_id = %s", (university, course, user_id))
               db.get_db().commit()
               flash('Profile info updated successfully.', 'success')

          # Profile Image handling
          elif form_type == 'profile_image':
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
                    return render_template ('student_profile.html', user=user, profile=profile)
               # save path to db
               elif profile_image_path:
                    cursor.execute("UPDATE user SET profile_image = %s WHERE user_id = %s", (profile_image_path, user_id))
                    db.get_db().commit()
                    flash('Profile image updated successfully.', 'success')
                    user, profile = get_student_user_and_profile(cursor, user_id)
                    cursor.close()
                    return render_template('student_profile.html', user=user, profile=profile)

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
                    return render_template ('student_profile.html', user=user, profile=profile)
               else:
                    flash(msg, "success")
                    user, profile = get_student_user_and_profile(cursor, user_id)
                    cursor.close()
                    return render_template ('student_profile.html', user=user, profile=profile)

          # Handle resume upload - similar to profile image upload
          elif form_type == "resume":
               resume_file = request.files.get('resume')
               cfg_resume = UPLOAD_CONFIG['resume']
               resume_path, resume_error = handle_file_upload(
               resume_file,
               subfolder=cfg_resume["subfolder"],
               username_or_id=user["username"],
               allowed_exts=cfg_resume["allowed_exts"],
               max_size_bytes=cfg_resume["max_size"],
               prefix=cfg_resume["prefix"]
               )
               # error message
               if resume_error:
                    flash(resume_error, "danger")
                    return render_template('student_profile.html', user=user, profile=profile)
               # update db
               elif resume_path:
                    cursor.execute("UPDATE student SET resume_path = %s WHERE user_id = %s", (resume_path, user_id))
                    db.get_db().commit()
                    flash('Resume updated successfully.', 'success')

    # Fetch profile data
     user, profile = get_student_user_and_profile(cursor, user_id)
     cursor.close()

     return render_template('student_profile.html', user=user, profile=profile)
