-- Create the Database
CREATE DATABASE Internlink;

-- Use the newly created database
USE Internlink;

-- Create the user Table
CREATE TABLE user (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100) NOT NULL,
    password_hash CHAR(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    profile_image VARCHAR(255),
    role ENUM('student', 'employer', 'admin') NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active' NOT NULL,
    PRIMARY KEY (user_id)
);

-- Create the student Table
CREATE TABLE student (
    student_id INT NOT NULL AUTO_INCREMENT, 
    user_id INT NOT NULL,
    university VARCHAR(100),
    course VARCHAR (100),
    resume_path VARCHAR(255),
    PRIMARY KEY (student_id),
    UNIQUE (user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Create the employer Table
CREATE TABLE employer (
    emp_id INT NOT NULL AUTO_INCREMENT, 
    user_id INT NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    company_description TEXT,
    website VARCHAR(100),
    logo_path VARCHAR(255),
    PRIMARY KEY (emp_id),
    UNIQUE (user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Create the internship Table
CREATE TABLE internship (
    internship_id INT NOT NULL AUTO_INCREMENT,
    company_id INT NOT NULL,
    title VARCHAR (100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(100),
    duration VARCHAR(50),
    skills_required TEXT,
    deadline DATE,
    stipend VARCHAR(50),
    number_of_opening INT,
    additonal_req TEXT,
    PRIMARY KEY (internship_id),
    UNIQUE (company_id),
    FOREIGN KEY (company_id) REFERENCES employer(emp_id)
);

-- Create the application Table
CREATE TABLE application (
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
    feedback TEXT,
    PRIMARY KEY (student_id, internship_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (internship_id) REFERENCES internship(internship_id)
);