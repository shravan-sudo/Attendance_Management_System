# My Python Web Application

This is a simple Python web application built with Flask.

## Installation



2. Install dependencies using 
`pip install mysql-connector-python`
`pip install Flask`
`pip install flask-sqlalchemy`
`pip install PyMySQL`
`pip install Jinja2`

3. Run the application using `app2.py`.

## Database Tables
1.create database `attendance`

 ** CREATE TABLE `attendance1` (
    id INT NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    faculty_name VARCHAR(255),
    parent_dept VARCHAR(255),
    branch VARCHAR(255),
    year INT,
    semester INT,
    hour TEXT,
    class_type VARCHAR(255),
    subject VARCHAR(255),
    topic VARCHAR(255),
    presentees TEXT,
    absentees TEXT,
    total INT DEFAULT 73,
    total_presentees INT,
    total_absentees INT
);

   **CREATE TABLE `authentication1` (
    id INT,
    timestamp TIMESTAMP(6),
    Username TEXT,
    password TEXT,
    Role TEXT
);

   **CREATE TABLE `removed_faculty` (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(50)
);
  **CREATE TABLE `removed_student` (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Student_roll VARCHAR(20),
    Student_name VARCHAR(255),
    Branch VARCHAR(100),
    Year INT,
    Semester INT
);

   **CREATE TABLE `student_info` (
    id INT,
    timestamp TIMESTAMP(6),
    Student_roll TEXT,
    Student_name TEXT,
    Branch TEXT,
    Year INT,
    Semester INT,
    phone_no TEXT,
    address TEXT
);

## Usage

- Navigate to `http://127.0.0.1:5000/firstpage.html` in your web browser.
- You will see the homepage of the application.


## Contact

For questions or support, contact [`kumarkushana1609@gmail.com` and `saikiranguguloth147@gmail.com`   ].








AMSKUCET : Username
Database name :AMSKUCET$attendance