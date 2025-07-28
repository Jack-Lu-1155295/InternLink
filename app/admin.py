from app import app
from app import db
from flask import redirect, render_template, session, url_for, request
from app.db import get_cursor

@app.route('/admin/home')
def admin_home():
     """Admin Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current admin user, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role']!='admin':
          return render_template('access_denied.html'), 403

     return render_template('admin_home.html')

@app.route('/admin/users', methods=['GET', 'POST'])
def user_management():
     # check logged in user is admin
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role']!='admin':
          return render_template('access_denied.html'), 403
     
     cursor = get_cursor()

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

     return render_template('admin_users.html', users=users, filters={
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
        'status': status
      })
