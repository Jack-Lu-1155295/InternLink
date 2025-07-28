from app import app
from app import db
from flask import redirect, render_template, session, url_for, request, flash
from app.db import get_cursor
import os
from werkzeug.utils import secure_filename

@app.route('/employer/home')
def employer_home():
     """employer Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current employer user, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role']!='employer':
          return render_template('access_denied.html'), 403

     return render_template('employer_home.html')

Image_Ext = {'png', 'jpg', 'jpeg'}

def allowedfile(filename, allowedext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedext

@app.route('/employer_profile', methods=['GET', 'POST'])
def employer_profile():
    # logged in as employer
    if 'loggedin' not in session or session.get('role') != 'employer':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    cursor = get_cursor()

    if request.method == 'POST':
          full_name = request.form.get('full_name')
          company_name = request.form.get('company_name')
          company_description = request.form.get('company_description')
          website = request.form.get('website')

          # Update full name in user table
          cursor.execute("UPDATE user SET full_name = %s WHERE user_id = %s", (full_name, user_id))

          # Update employer information: company_name, description, website
          cursor.execute("""
               UPDATE employer SET company_name = %s, company_description = %s, website = %s 
               WHERE user_id = %s
               """, (company_name, company_description, website, user_id))

          # Logo upload
          logo_file = request.files.get('logo')
          logo_path = None
          if logo_file and allowedfile(logo_file.filename, Image_Ext):
               max_image_size = 1 * 1024 * 1024
               logo_file.seek(0, os.SEEK_END)
               image_file_size = logo_file.tell()
               logo_file.seek(0)
               
               if image_file_size > max_image_size:
                    flash('Image file exceeds 1MB size limit.', 'danger')
                    return render_template('employer_profile.html', user_id=user_id, full_name=full_name, company_name=company_name, company_description=company_description, website=website)

               else:
                    ext = logo_file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(f"logo_{user_id}.{ext}")
                    logo_path = os.path.join('static', 'logos', filename).replace('\\', '/')
                    logo_file.save(logo_path)

                    try:
                         cursor.execute("""
                              UPDATE employer SET logo_path = %s WHERE user_id = %s
                              """, (logo_path, user_id))  
                         db.get_db().commit()
                         flash('Your company logo has been updated successfully.', 'success')

                    except Exception as e:
                         print("Logo path update error:", e)
                         flash('Failed to update logo in database.','danger')
                         return render_template('employer_profile.html', user_id=user_id, full_name=full_name, company_name=company_name, company_description=company_description, website=website)
          else:
               flash('Invalid logo format. Only JPG, PNG, JPEG less than 1 MB allowed.', 'danger')
               return render_template('employer_profile.html', profile={
                    'full_name': full_name,
                    'email': session.get('email'),
                    'company_name': company_name,
                    'company_description': company_description,
                    'website': website,
                    'logo_path': None})
    
    # Fetch profile data
    cursor.execute("""
          SELECT u.full_name, u.email, u.profile_image,
                    e.company_name, e.company_description, e.website, e.logo_path
          FROM user u
          JOIN employer e ON u.user_id = e.user_id
          WHERE u.user_id = %s
          """, (user_id,))
    profile = cursor.fetchone()
    cursor.close()

    return render_template('employer_profile.html', profile=profile)
