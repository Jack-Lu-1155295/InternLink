from app import app
from app import db
from flask import redirect, render_template, request, session, url_for, flash
from app.db import get_cursor
from flask_bcrypt import Bcrypt

@app.route('/browseinternships')
def browse_internships():
    # only student and admin can access
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    user_id = session.get('user_id')
    
    if session['role'] not in ['student', 'employer', 'admin']:
        return render_template('access_denied.html'), 403

    # get required information 
    location = request.args.get('location', '')
    duration = request.args.get('duration', '')
    skills = request.args.get('skills', '')

    query = """
        SELECT i.*, e.company_name
        FROM internship i
        JOIN employer e ON i.company_id = e.emp_id
        WHERE i.location LIKE %s AND i.duration LIKE %s AND
              (i.skills_required LIKE %s OR i.title LIKE %s OR i.description LIKE %s)
    """

    filters = (f"%{location}%", f"%{duration}%", f"%{skills}%", f"%{skills}%", f"%{skills}%")

    cursor = get_cursor()
    
    # only show internships posted by the logged in employer
    if role == 'employer':
        cursor.execute("SELECT emp_id FROM employer WHERE user_id = %s", (user_id,))
        employer = cursor.fetchone() 
        company_id = employer['emp_id']
        query += " AND i.company_id = %s"
        filters += (company_id,)

    cursor.execute(query, filters)
    internships = cursor.fetchall()
    cursor.close()

    return render_template('browse_internships.html', internships=internships)

@app.route('/applications', methods=['GET', 'POST'])
def view_applications():
    # check login status
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    user_id = session.get('user_id')
    cursor = get_cursor()

    name_query=request.args.get('name', '')
    title_query = request.args.get('title', '')
    status_query = request.args.get('status', '')

    # when a student logged in, he should only see his own applications
    if role == 'student':
        # get student_id using user_id
        cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return render_template('access_denied.html'), 403

        student_id = result['student_id']

        cursor.execute("""
            SELECT i.title, i.location, i.duration, i.deadline,
                   a.status, a.feedback
            FROM application a
            JOIN internship i ON a.internship_id = i.internship_id
            WHERE a.student_id = %s
            ORDER BY i.deadline DESC
        """, (student_id,))
        
        applications = cursor.fetchall()
        cursor.close()
        return render_template('student_applications.html', applications=applications)
    
    # when an admin logged in, he should be able to see all applications.
    elif role == 'admin':
        admin_query = """
            SELECT a.student_id, u.full_name, i.title, i.location, i.duration, i.deadline,
                   a.status, a.feedback, a.cover_letter, i.internship_id
            FROM application a
            JOIN internship i ON a.internship_id = i.internship_id
            JOIN student s ON a.student_id = s.student_id
            JOIN user u ON s.user_id = u.user_id
            WHERE u.full_name LIKE %s AND i.title LIKE %s AND a.status LIKE %s
            ORDER BY i.deadline DESC
        """
        
        filters = (f"%{name_query}%", f"%{title_query}%", f"%{status_query}%")
        cursor.execute(admin_query, filters)
        applications = cursor.fetchall()

        if request.method == 'POST':
            app_student_id = request.form.get('student_id')
            internship_id = request.form.get('internship_id')
            new_status = request.form.get('status')
            feedback = request.form.get('feedback', None)

            cursor.execute("""
                UPDATE application
                SET status = %s, feedback = %s
                WHERE student_id = %s AND internship_id = %s
            """, (new_status, feedback, app_student_id, internship_id))
            db.get_db().commit()
            flash('Application status updated successfully.', 'success')
            return redirect(url_for('view_applications'))

        cursor.close()
        return render_template('admin_applications.html', applications=applications)
    

    #when an employer logged in, he should be able to view applications to internships posted by him.
    elif role == 'employer':
        cursor.execute("SELECT emp_id FROM employer WHERE user_id = %s", (user_id,))
        employer = cursor.fetchone()
        company_id = employer['emp_id']

        query = """
            SELECT a.student_id, u.full_name, i.title, i.internship_id, a.status, a.feedback, a.cover_letter
            FROM application a
            JOIN internship i ON a.internship_id = i.internship_id
            JOIN student s ON a.student_id = s.student_id
            JOIN user u ON s.user_id = u.user_id
            WHERE i.company_id = %s AND u.full_name LIKE %s AND i.title LIKE %s AND a.status LIKE %s
            ORDER BY i.title ASC
        """

        filters = (company_id, f"%{name_query}%", f"%{title_query}%", f"%{status_query}%")

        cursor.execute(query, filters)
        applications = cursor.fetchall()

        if request.method == 'POST':
            app_student_id = request.form.get('student_id')
            internship_id = request.form.get('internship_id')
            new_status = request.form.get('status')
            feedback = request.form.get('feedback', None)

            cursor.execute("""
                UPDATE application
                SET status = %s, feedback = %s
                WHERE student_id = %s AND internship_id = %s
            """, (new_status, feedback, app_student_id, internship_id))
            db.get_db().commit()
            flash('Application status updated successfully.', 'success')
            return redirect(url_for('view_applications'))

        cursor.close()
        return render_template('employer_applications.html', applications=applications)

bcrypt = Bcrypt(app)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    role = session.get('role')
    cursor = get_cursor()
    
    if request.method == "POST":
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # get the current hashed password
        cursor.execute("SELECT password_hash FROM user WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        # password validation
        if not result:
            flash("User not found", "danger")
            return render_template('change_password.html')
        elif not current_password or not new_password or not confirm_password:
            flash("All fields are required", "danger")
            return render_template('change_password.html')
        elif not bcrypt.check_password_hash(result['password_hash'], current_password):
            flash("Current password is incorrect.", "danger")
            return render_template('change_password.html')
        elif new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return render_template('change_password.html')
        elif bcrypt.check_password_hash(result['password_hash'], new_password):
            flash("New password cannot be the same as the current password.", "warning")
            return render_template('change_password.html')
        elif len(new_password) < 8:
            flash("New password must be at least 8 characters.", "warning")
            return render_template('change_password.html')
        
        # update password
        else:
            hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cursor.execute("UPDATE user SET password_hash = %s WHERE user_id = %s", (hashed, user_id))
            db.get_db().commit()
            flash("Password changed successfully.", "success")
        cursor.close()
    
        if role == 'student':
            return redirect(url_for('student_home'))
        if role == 'emplyer':
            return redirect(url_for('employer_home'))
        if role == 'admin':
            return redirect(url_for('admin_home'))

    cursor.close()
    return render_template('change_password.html')


