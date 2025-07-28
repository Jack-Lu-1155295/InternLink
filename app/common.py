from app import app
from app import db
from flask import redirect, render_template, request, session, url_for
from app.db import get_cursor

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


@app.route('/applications')
def view_applications():
    # check login status
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    user_id = session.get('user_id')
    cursor = get_cursor()

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

    # when an admin logged in, he should be able to see all applications.
    elif role == 'admin':
        cursor.execute("""
            SELECT u.full_name, i.title, i.location, i.duration, i.deadline,
                   a.status, a.feedback, a.cover_letter
            FROM application a
            JOIN internship i ON a.internship_id = i.internship_id
            JOIN student s ON a.student_id = s.student_id
            JOIN user u ON s.user_id = u.user_id
            ORDER BY i.deadline DESC
        """)

    else:
        cursor.close()
        return render_template('access_denied.html'), 403

    applications = cursor.fetchall()
    cursor.close()

    template = 'student_applications.html' if role == 'student' else 'admin_applications.html'
    return render_template(template, applications=applications)