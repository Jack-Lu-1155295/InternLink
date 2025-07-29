# InternLink – Internship Management System
Built using Flask and MySQL, InternLink is a role-based web application for internship management.

## Main Features

- student signup, login, uploading resume and profile image
- internship browsing and application
- employer profile management and internship management
- admin user management
- role-based access control
- secure password hashing


## Installation and Setup

### Repo 
https://github.com/Jack-Lu-1155295/InternLink

### Create python virtual environment
python -m venv 

### Activate the environment
.venv\Scripts\activate

### Install requirements

pip install -r requirements.txt

### Configure your local database
In connect.py
update with your local MySQL credentials
dbuser = "your_db_user"
dbpass = "your_db_password"
dbhost = "localhost"
dbport = 3306
dbname = "internlink"

### Database creation
run databse creation script.sql to create the database 'internlink'

run InternLink DB population.sql to populate data

## Running the app

python run.py

Open your browser and visit http://127.0.0.1:5000