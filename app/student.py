from app import app
from app import db
from flask import redirect, render_template, session, url_for
from flask import request, flash
from app.db import get_cursor
from werkzeug.utils import secure_filename
import os

@app.route('/student/home')
def student_home():
     """student Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current student, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     # Note: You'll need to use "logged in" and role checks like the ones below
     # on every single endpoint that should be restricted to logged-in users,
     # or users with a certain role. Otherwise, anyone who knows the URL can
     # access that page.
     #
     # In this example we've just repeated the code everywhere (you'll see the
     # same checks in staff.py and admin.py), but it would be a great idea to
     # extract these checks into reusable functions. You could place them in
     # user.py with the rest of the login system, for example, and import them
     # into other modules as necessary.
     #
     # One common way to implement login and role checks in Flask is with "View
     # Decorators", such as the "login_required" example in the official
     # tutorial [1]. If you choose to use that approach, you'll need to adapt
     # it a little to our project, as we don't store the username in `g.user`.
     #
     # References:
     # [1] https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/

     if 'loggedin' not in session:
          # The user isn't logged in, so redirect them to the login page.
          return redirect(url_for('login'))
     elif session['role']!='student':
          # The user isn't logged in with a student account, so return an
          # "Access Denied" page instead. We don't do a redirect here, because
          # we're not sending them somewhere else: just delivering an
          # alternative page.
          # 
          # Note: the '403' below returns HTTP status code 403: Forbidden to the
          # browser, indicating that the user was not allowed to access the
          # requested page.
          return render_template('access_denied.html'), 403

     # The user is logged in with a student account, so render the student
     # homepage as requested.
     return render_template('student_home.html')

def allowedfile(filename, allowedext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedext

@app.route('/student/apply/<int:internship_id>', methods=['GET', 'POST'])
def apply_internship(internship_id):

     # student login
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role'] != 'student':
          return render_template('access_denied.html'), 403  
     
     user_id=session.get('user_id')
     cursor=get_cursor()

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

     # Resume 
     Resume_Ext = {'pdf'}

     if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '') or None
        resume_file = request.files.get('resume') or None

        resume_path = student_info['resume_path'] or None 
        
        if resume_file and resume_file.filename:
          if allowedfile(resume_file.filename, Resume_Ext):
               max_resume_size = 5 * 1024 * 1024
               resume_file.seek(0, os.SEEK_END)
               resume_file_size = resume_file.tell()
               resume_file.seek(0)
                    
               if resume_file_size > max_resume_size:
                    flash('Resume file exceeds 5MB size limit.', 'danger')
                    return render_template('apply_internship.html', internship=internship, student_id=student_id, student_info=student_info)
                    
               else:
                    ext = resume_file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(f"resume_{session['username']}.{ext}")
                    resume_path = os.path.join('static/resumes', filename)
                    resume_file.save(resume_path)

                    try:
                         cursor.execute("""
                         UPDATE student SET resume_path = %s WHERE student_id = %s
                         """, (resume_path, student_id))
                         db.get_db().commit()
                    except Exception as e:
                         print("Resume path update error:", e)
                         flash('Failed to update resume in database.','danger')
                         return render_template('apply_internship.html',internship=internship, student_id=student_id, student_info=student_info)
          else:
               flash('Invalid resume format. Only PDF allowed.', 'danger')
               return render_template('apply_internship.html', internship=internship, student_id=student_id, student_info=student_info)

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
               return render_template('apply_internship.html', internship=internship, student_id=student_id, student_info=student_info)

        cursor.close()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('student_home'))
     
     return render_template('apply_internship.html', internship=internship, student_id=student_id, student_info=student_info)


