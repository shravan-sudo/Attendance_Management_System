
import mysql.connector
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from io import BytesIO
from collections import Counter
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from urllib.parse import quote_plus
import pymysql
from jinja2 import Environment
def zip_lists(list1, list2):
    return zip(list1, list2)

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip_lists

# Encode the password
password = quote_plus('Kirannayak@1')

# Construct the database URI with the encoded password
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{password}@localhost:3306/attendance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Attendance(db.Model):
    __tablename__ = 'attendance1'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    branch = db.Column(db.String(50))
    semester = db.Column(db.Integer)
    class_type = db.Column(db.String(50))
    subject = db.Column(db.String(100))
    presentees = db.Column(db.String(100))
    # Add other columns as needed

class StudentInfo(db.Model):
    __tablename__ = 'student_info'

    id = db.Column(db.Integer, primary_key=True)
    Student_roll = db.Column(db.String(20), unique=True)
    Student_name = db.Column(db.String(100))
    year = db.Column(db.Integer)
    branch = db.Column(db.String(50))
    semester = db.Column(db.Integer)
    # Add other columns as needed

# Route to render the HTML page
@app.route('/ViewAttendance.html')
def view_attendance():
    # Fetch unique values from the database for each dropdown
    years = Attendance.query.with_entities(Attendance.year).distinct().all()
    branches = Attendance.query.with_entities(Attendance.branch).distinct().all()
    semesters = Attendance.query.with_entities(Attendance.semester).distinct().all()
    classtypes = Attendance.query.with_entities(Attendance.class_type).distinct().all()

    return render_template('ViewAttendance.html', years=years, branches=branches, semesters=semesters, classtypes=classtypes)

# New route to handle form submission
@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Retrieve form data from the submitted form
  
    Student_roll = request.form.get('Student_roll')

    print(f"St:{Student_roll}")
    year = request.form.get('year')
    branch = request.form.get('branch')
    semester = request.form.get('semester')
    classtype=request.form.get('classtype')

    print(f"Querying for Student Roll: {Student_roll}")
    # Query student information from the 'student_info' table
    student = StudentInfo.query.filter_by(Student_roll=Student_roll).first()
   
    if student:
        student.year = year
        student.branch = branch
        student.semester = semester
        student.classtype=classtype
        student.Student_roll=Student_roll
        # If the student is found, render a new template with the student's information
        # return render_template('student_info.html', student=student)
        return filter_subjects(student)
        # return render_template('attendance_table.html', student=student)
    else:
        # If the student is not found, render an error template or handle accordingly
        return render_template('student_not_found.html')
    


def filter_subjects(student):
 try:
    selected_year = student.year
    selected_branch = student.branch
    selected_semester = student.semester
    selected_class_type = student.classtype
    student_roll_last_2_digits = student.Student_roll[-3:-1] if student.Student_roll[-1].isalpha() else student.Student_roll[-2:]

    print(f"Selected Filters: Year={selected_year}, Branch={selected_branch}, Semester={selected_semester}, Class Type={selected_class_type},{student_roll_last_2_digits}")

    
    subjects = Attendance.query.with_entities(Attendance.subject).filter(
        Attendance.year == selected_year,
        Attendance.branch == selected_branch,
        Attendance.semester == selected_semester,
        Attendance.class_type == selected_class_type).all()


   
    matching_subjects = []
    for subject in subjects:
       
        matching_subjects.append(subject)
    subject_counts = Counter(matching_subjects)

# Create a dictionary to store subjects and their counts
    subjects_with_counts = {}

# Print the counts for each subject and store in the dictionary
    for subject, count in subject_counts.items():
      print(f"{subject}: {count} times")
      subjects_with_counts[subject] = count
       
    matching_subjects = list(set(matching_subjects))

    print(f"Subjects are:{matching_subjects}")
    cleaned_matching_subjects = [subject[0] for subject in matching_subjects]

    print(cleaned_matching_subjects)
    total_classes=len(subjects)
    print(f"Number of classes found: {len(subjects)}")

   
    subject_counts = {}

    for subjectt in cleaned_matching_subjects:
     if isinstance(subjectt, tuple):
        # If subjectt is a tuple, take the first element
        subjectt = subjectt[0]

     subjectss = Attendance.query.filter(
        Attendance.year == selected_year,
        Attendance.branch == selected_branch,
        Attendance.semester == selected_semester,
        Attendance.class_type == selected_class_type,
        Attendance.subject == subjectt,
        Attendance.presentees.contains(student_roll_last_2_digits)
      )

     count_rows = subjectss.with_entities(func.count()).scalar()
    #  attended_classes=len(subjectss)
     print(f"Number of classes found: {len(subjects)}")
    # Store the count for each subject in the dictionary
     subject_counts[subjectt] = count_rows
     
# Print counts for each subject
    sum=0
    for subject, count in subject_counts.items():
     print(f"Student roll {student_roll_last_2_digits} found in {count} rows for subject {subject}.")
     sum+=count
    print(sum)

    each_subject_counts = {}

    for subject in cleaned_matching_subjects:
       if isinstance(subject, tuple):
        # If subject is a tuple, take the first element
          subject = subject[0]

       subjects_query = Attendance.query.filter(
          Attendance.year == selected_year,
          Attendance.branch == selected_branch,
          Attendance.semester == selected_semester,
          Attendance.class_type == selected_class_type,
          Attendance.subject == subject,
       )

       count_rows = subjects_query.with_entities(func.count()).scalar()
    
    # Store the count for each subject in the dictionary
       each_subject_counts[subject] = count_rows

# Print counts for each subject
    for subject, count in each_subject_counts.items():
      print(f"Count for subject {subject}: {count}")
    # Assuming you want to pass 'subjects' and 'student' to the template
    # return render_template('attendance_table.html', subjects=cleaned_matching_subjects, student=student)
    # Assuming you want to pass 'subjects' and 'student' to the template
   # Assuming you want to pass 'subjects', 'subject_counts', 'total_classes', and 'sum' to the template
    return render_template('attendance_table.html', subjects=cleaned_matching_subjects, student=student, subject_counts=subject_counts, total_classes=total_classes, attended_classes=sum, each_subject_counts=each_subject_counts)

 except Exception as e:
        print(f"An error occurred: {e}")
        return redirect('/student_not_found.html')


# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kirannayak@1',
    'database': 'attendance'
}

def connect_db():
    conn = mysql.connector.connect(**db_config)
    return conn

def get_unique_column_values(column_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT {column_name} FROM attendance1")
    values = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return values

def get_matching_rows(branch, year, semester, faculty_name):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    # Base query
    query = "SELECT * FROM attendance1 WHERE 1 = 1"

    # Append conditions for selected dropdown values
    params = []
    if branch:
        query += " AND branch = %s"
        params.append(branch)
    if year:
        query += " AND year = %s"
        params.append(year)
    if semester:
        query += " AND semester = %s"
        params.append(semester)
    if faculty_name:
        query += " AND faculty_name = %s"
        params.append(faculty_name)

    cursor.execute(query, tuple(params))
    matching_rows = cursor.fetchall()
    
    column_names = cursor.column_names
    cursor.close()
    conn.close()
    return matching_rows, column_names

@app.route('/index.html')
def index():
    # Populate dropdown values from the database
    branch_values = get_unique_column_values('branch')
    year_semester_values = get_unique_column_values('year')
    semester_values = get_unique_column_values('semester')
    teacher_values = get_unique_column_values('faculty_name')
    return render_template('index.html', branch_values=branch_values, year_semester_values=year_semester_values, semester_values=semester_values, teacher_values=teacher_values)

@app.route('/get_matching_rows', methods=['POST'])
def get_matching_rows_route():
    
        selected_branch = request.form.get('selected_branch')
        selected_year_semester = request.form.get('selected_year_semester')
        selected_semester = request.form.get('selected_semester')
        selected_teacher = request.form.get('selected_teacher')

        matching_rows, column_names = get_matching_rows(selected_branch, selected_year_semester, selected_semester, selected_teacher)

        if matching_rows is not None:
            if len(matching_rows) > 0:
                return jsonify(matching_rows=matching_rows, column_names=column_names)
            else:
                print("No matching rows found")
                return jsonify(error="No matching rows found")
        else:
            print("Matching rows is None")
            return jsonify(error="An error occurred while fetching matching rows")
    




# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kirannayak@1',
    'database': 'attendance'
}

# Function to create a connection to the MySQL database
def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        print("Connected to MySQL database")
    except mysql.connector.Error as e:
        print(e)
    return conn


# Route to render the index page (firstpage.html)
@app.route('/')
def firstpage():
    return render_template('firstpage.html')

# Route to render the index page (firstpage.html)
@app.route('/firstpage.html')
def first_page():
    return render_template('firstpage.html')

# Route to render the about page (about.html)
@app.route('/about.html')
def about():
    return render_template('about.html')

# Route to render the contact page (contact.html)
@app.route('/contact.html')
def contact():
    return render_template('contact.html')

# Route to render the admin login page (admin_login.html)
@app.route('/admin_login.html')
def admin_login():
    return render_template('admin_login.html')

# Route to render the faculty login page (FacultyLogin.html)
@app.route('/FacultyLogin.html')
def faculty_login():
    return render_template('FacultyLogin.html')

# Route to render the student login page (Studentlogin.html)
@app.route('/Studentlogin.html')
def student_login():
    # Fetch unique values from the database for each dropdown
    years = Attendance.query.with_entities(Attendance.year).distinct().all()
    branches = Attendance.query.with_entities(Attendance.branch).distinct().all()
    semesters = Attendance.query.with_entities(Attendance.semester).distinct().all()
    classtypes = Attendance.query.with_entities(Attendance.class_type).distinct().all()

    return render_template('Studentlogin.html', years=years, branches=branches, semesters=semesters, classtypes=classtypes)

# New route to handle form submission
@app.route('/submit_form1', methods=['POST'])
def submit_form1():
    # Retrieve form data from the submitted form
  
    Student_roll = request.form.get('Student_roll')

    print(f"St:{Student_roll}")
    year = request.form.get('year')
    branch = request.form.get('branch')
    semester = request.form.get('semester')
    classtype=request.form.get('classtype')

    print(f"Querying for Student Roll: {Student_roll}")
    # Query student information from the 'student_info' table
    student = StudentInfo.query.filter_by(Student_roll=Student_roll).first()
   
    if student:
        student.year = year
        student.branch = branch
        student.semester = semester
        student.classtype=classtype
        student.Student_roll=Student_roll
        # If the student is found, render a new template with the student's information
        # return render_template('student_info.html', student=student)
        return filter_subjects(student)
        # return render_template('attendance_table.html', student=student)
    else:
        # If the student is not found, render an error template or handle accordingly
        return render_template('student_not_found.html')
    

# Route for handling admin login form submission
@app.route('/authenticateAdmin', methods=['POST'])
def authenticate_admin_route():
    username = request.form['username']
    password = request.form['password']
    if authenticate_admin(username, password):
        return redirect(url_for('success_page', username=username))
    else:
        return redirect(url_for('login_page'))


@app.route('/success_page')
def success_page():
    username = request.args.get('username')
    role = get_role(username)
    if role == "Admin":
        return redirect(url_for('admin_page'))
    elif role == "Teacher":
        return redirect(url_for('success1'))
    else:
        return redirect(url_for('login_page'))

# # Route for successful login
# @app.route('/success')
# def success():
#     return redirect(url_for('admin_page'))

# Route for serving the admin page after successful login
@app.route('/admin')
def admin_page():
    return render_template('Admin.html')

# Route for serving the teacher page after successful login
@app.route('/success1')
def success1():
    return render_template('Faculty.html')

@app.route('/login_page')
def login_page():
    return render_template('firstpage.html')

def get_role(username):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kirannayak@1",
        database="attendance"
    )
    
    cursor = conn.cursor()
    query = "SELECT role FROM authentication1 WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

# Function to authenticate admin login
def authenticate_admin(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM authentication1 WHERE Username = %s AND password = %s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return True
    else:
        return False

# Route to render the take attendance page (TakeAttendance.html)
@app.route('/TakeAttendance.html')
def take_attendance():
    return render_template('TakeAttendance.html')


# Function to calculate absentees
def calculate_absentees(presentees, total):
    presentees_list = presentees.split(',') if presentees else []
    total_students = int(total)
    all_students = set(range(1, total_students + 1))
    presentees_set = set(map(int, presentees_list))
    absentees_set = all_students - presentees_set
    absentees = ','.join(map(str, absentees_set))
    total_presentees = len(presentees_set)
    total_absentees = len(absentees_set)
    return absentees, total_presentees, total_absentees

# Update the table with absentees
def update_absentees():
    cursor.execute("SELECT id, presentees, total FROM attendance1")
    rows = cursor.fetchall()
    for row in rows:
        id, presentees, total = row
        absentees, total_presentees, total_absentees = calculate_absentees(presentees, total)
        cursor.execute("UPDATE attendance1 SET absentees = %s, total_presentees = %s, total_absentees = %s WHERE id = %s", (absentees, total_presentees, total_absentees, id))
    conn.commit()

@app.route('/TakeAttendance.html')
def TakeAttendance():
    return render_template('TakeAttendance.html')

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Kirannayak@1',
    database='attendance'
)
cursor = conn.cursor()

@app.route('/TakeAttendance/', methods=['POST'])
def take_attendance_post():
    if request.method == 'POST':
        # Fetching data from the form
        faculty_name = request.form['faculty_name']
        parent_dept = request.form['parent_dept']
        branch = request.form['branch']
        year = request.form['year']
        semester = request.form['semester']
        hour = request.form['hour']
        class_type = request.form['class_type']
        subject = request.form['subject']
        topic = request.form['topic']
        presentees = request.form['presentees']
        # total_students = request.form['total_students']

        # Inserting data into MySQL
        insert_query = "INSERT INTO attendance1 (faculty_name, parent_dept, branch, year, semester, hour, class_type, subject, topic, presentees) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (faculty_name, parent_dept, branch, year, semester, hour, class_type, subject, topic, presentees))
        conn.commit()
        update_absentees() # Update absentees after inserting new attendance
        return redirect(url_for('success'))

@app.route('/success')
def success():
    return 'Data inserted successfully!'

# Function to fetch data from the database
def get_students():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Kirannayak@1',
                                 database='attendance',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM student_info")
            students = cursor.fetchall()
    
    return students

# Route to display students list
@app.route('/students_list.html')
def display_students_list():
    students = get_students()
    return render_template('students_list.html', students=students)

# Function to fetch data from the database
def get_authentication_data():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Kirannayak@1',
                                 database='attendance',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM authentication1")
            authentication_data = cursor.fetchall()
    
    return authentication_data

# Route to display authentication data
@app.route('/authentication_data.html')
def display_authentication_data():
    authentication_data = get_authentication_data()
    return render_template('authentication_data.html', authentication_data=authentication_data)

# Route to render the teacherinfo page (teacherinfo.html)
@app.route('/teacherinfo.html')
def manage_faculty_info():
    # Code to handle faculty information CSV
    return render_template('teacherinfo.html')

# Route to handle form submission for adding or removing admin credentials


@app.route('/admin', methods=['POST'])
def admin():
    executed_block = None
    action_result = None
    if request.method == 'POST':
        conn = create_connection()
        with conn:
            action = request.form.get('action')
            if action == 'ADD':
                executed_block = 'Add block executed'
                username = request.form['Username']
                password = request.form['password']
                role = request.form['Role']
                insert_sql = '''INSERT INTO authentication1(Username, password, Role)
                                VALUES(%s, %s, %s)'''
                data_tuple = (username, password, role)
                try:
                    cursor = conn.cursor()
                    cursor.execute(insert_sql, data_tuple)
                    conn.commit()
                    action_result = "Added to authentication1 table."
                except mysql.connector.Error as e:
                    action_result = f"Error adding to authentication1 table: {e}"
            elif action == 'REMOVE':
                executed_block = 'Remove block executed'
                username = request.form['Username']
                password = request.form['password']
                role = request.form['Role']

                select_sql = 'SELECT Username, password, Role FROM authentication1 WHERE Username = %s AND password = %s AND Role = %s'
                delete_sql = 'DELETE FROM authentication1 WHERE Username = %s AND password = %s AND Role = %s'
                try:
                    cursor = conn.cursor()
                    cursor.execute(select_sql, (username, password, role))
                    removed_faculty_data = cursor.fetchall()
                    cursor.execute(delete_sql, (username, password, role))
                    conn.commit()
                    action_result = "Removed from authentication1 table and added to removed_faculty table."

                    if removed_faculty_data:
                        insert_removed_sql = '''INSERT INTO removed_faculty(Username, password, Role)
                                               VALUES(%s, %s, %s)'''
                        cursor.executemany(insert_removed_sql, removed_faculty_data)
                        conn.commit()
                except mysql.connector.Error as e:
                    action_result = f"Error removing from authentication1 table: {e}"

    return render_template('result.html', executed_block=executed_block, action_result=action_result)


# Route to render the teacherinfo page (teacherinfo.html)
@app.route('/studentinfo.html')
def student_info():
    # Code to handle faculty information CSV
    return render_template('studentinfo.html')

#e to handle form submission for adding or removing student info
@app.route('/student', methods=['POST'])
def student():
    executed_block = None
    action_result = None
    
    if request.method == 'POST':
        conn = create_connection()
        if conn is None:
            return "Error: Could not connect to the database."
        
        with conn:
            action = request.form.get('action')
            if action == 'ADD':
                executed_block = 'Add block executed'
                student_roll = request.form['Student_roll']
                student_name = request.form['Student_name']
                year = request.form['Year']
                branch = request.form['Branch']
                semester = request.form['Semester']
                
                try:
                    # Ensure 'Year' value is an integer
                    year = int(year)
                except ValueError:
                    return "Error: Year must be an integer."
                
                insert_sql = '''INSERT INTO student_info(Student_roll, Student_name, Year, Branch, Semester, timestamp)
                                VALUES(%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)'''
                data_tuple = (student_roll, student_name, year, branch, semester)
                
                try:
                    cursor = conn.cursor()
                    cursor.execute(insert_sql, data_tuple)
                    conn.commit()
                    action_result = "Added to student_info table."
                except mysql.connector.Error as e:
                    action_result = f"Error adding to student_info table: {e}"
                    
            elif action == 'REMOVE':
                executed_block = 'Remove block executed'
                student_roll = request.form['Student_roll']
                select_sql = 'SELECT * FROM student_info WHERE Student_roll = %s'
                delete_sql = 'DELETE FROM student_info WHERE Student_roll = %s'
                
                try:
                    cursor = conn.cursor()
                    cursor.execute(select_sql, (student_roll,))
                    removed_student_data = cursor.fetchall()
                    
                    cursor.execute(delete_sql, (student_roll,))
                    conn.commit()
                    action_result = "Removed from student_info table and added to removed_students table."
                    
                    if removed_student_data:
                        removed_student_info = removed_student_data[0]
                        removed_student_roll = removed_student_info[2]
                        removed_student_name = removed_student_info[3]
                        removed_year = removed_student_info[5]
                        removed_branch = removed_student_info[4]
                        removed_semester = removed_student_info[6]
                        
                        insert_removed_sql = '''INSERT INTO removed_student(Student_roll, Student_name, Year, Branch, Semester, timestamp)
                                                VALUES(%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)'''
                        removed_data_tuple = (removed_student_roll, removed_student_name, removed_year, removed_branch, removed_semester)
                        cursor.execute(insert_removed_sql, removed_data_tuple)
                        conn.commit()
                except mysql.connector.Error as e:
                    action_result = f"Error removing from student_info table: {e}"
    
    return render_template('result.html', executed_block=executed_block, action_result=action_result)

# Function to fetch data from the database
def get_removed_students():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Kirannayak@1',
                                 database='attendance',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM removed_student")
            removed_students = cursor.fetchall()
    
    return removed_students

# Route to display removed students
@app.route('/removed_students.html')
def display_removed_students():
    removed_students = get_removed_students()
    return render_template('removed_students.html', removed_students=removed_students)

# Function to fetch data from the database
def get_removed_faculty():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Kirannayak@1',
                                 database='attendance',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM removed_faculty")
            removed_faculty = cursor.fetchall()
    
    return removed_faculty

# Route to display removed faculty
@app.route('/removed_faculty.html')
def display_removed_faculty():
    removed_faculty = get_removed_faculty()
    return render_template('removed_faculty.html', removed_faculty=removed_faculty)

# Route to render the view attendance page (ViewAttendance.html)
@app.route('/ViewAttendance.html')
def viewattendance():
    return render_template('ViewAttendance.html')

@app.route('/index.html')
def faculty_teaching_diary():
    return render_template('index.html')

@app.route('/submit_form_second', methods=['POST'])
def submit_form_second():
    # Retrieve form data from the submitted form
    year = request.form.get('year')
    branch = request.form.get('branch')
    semester = request.form.get('semester')
    classtype = request.form.get('classtype')
    
    # Check if form data is received correctly
    print("Received Form Data:")
    print("Year:", year)
    print("Branch:", branch)
    print("Semester:", semester)
    print("Class Type:", classtype)
    
    # Query student information from the 'student_info' table
    students = StudentInfo.query.filter_by(year=year, branch=branch, semester=semester).all()
    
    # Check if students are retrieved
    if students:
        # Extract student roll numbers and store them in a list
        student_roll_numbers = [student.Student_roll for student in students]
        print("Student Roll Numbers:", student_roll_numbers)
        return redirect(url_for('another_route', year=year, branch=branch, semester=semester, classtype=classtype, roll_numbers=student_roll_numbers))
    else:
        print("No students found for the given criteria.")
        # Handle the case where no students are found
        return "No students found for the given criteria."

@app.route('/another_route', methods=['GET'])
def another_route():
    # Retrieve parameters from the URL
    year = request.args.get('year')
    branch = request.args.get('branch')
    semester = request.args.get('semester')
    classtype = request.args.get('classtype')
    roll_numbers = request.args.getlist('roll_numbers')
    
    print(f"Received Data - Year: {year}, Branch: {branch}, Semester: {semester}, Class Type: {classtype}, Roll Numbers: {roll_numbers}")
    
    # Process the data and return a response
    # You can add your logic here
    subjects1 = Attendance.query.with_entities(Attendance.subject).filter(
        Attendance.year == year,
        Attendance.branch == branch,
        Attendance.semester == semester,
        Attendance.class_type == classtype).all()


   
    matching_subjects1 = []
    for subject in subjects1:
       
        matching_subjects1.append(subject)
    subject_counts1 = Counter(matching_subjects1)

# Create a dictionary to store subjects and their counts
    subjects_with_counts1 = {}
    to=[]
# Print the counts for each subject and store in the dictionary
    for subject, count in subject_counts1.items():
      to.append(count)
      print(f"{subject}: {count} times")
      subjects_with_counts1[subject] = count
       
    matching_subjects1 = list(set(matching_subjects1))

    print(f"Subjects are:{matching_subjects1}")
    cleaned_matching_subjects1 = [subject[0] for subject in matching_subjects1]

    print(cleaned_matching_subjects1)
    total_classes1=len(subjects1)
    print(f"Number of classes found: {len(subjects1)}")

   
    # subject_counts = {}
    srno = []
    for i in roll_numbers:
        # i = i[-3:-1]
        if i[-1].isalpha():
           i = i[-3:-1]
           srno.append(i)
        else:
           i = i[-2:]
           srno.append(i)
    print(srno)
        # student_roll_last_2_digits = student.Student_roll[-3:-1] if student.Student_roll[-1].isalpha() else student.Student_roll[-2:]

    # student_roll_last_2_digits = roll_numbers[-3:-1] if roll_numbers[-1].isalpha() else roll_numbers[-2:]
    # print(student_roll_last_2_digits)
    
    # roll_numbers = ['01', '02', '03']  # Replace with your array of roll numbers
    attendance_data = {}  # Initialize a dictionary to store attendance data for each roll number
    tarr=[]
    for roll_number in roll_numbers:
      subject_counts = {}
      student_roll_last_2_digits = roll_number[-3:-1] if roll_number[-1].isalpha() else roll_number[-2:]

      for subjectt in cleaned_matching_subjects1:
        if isinstance(subjectt, tuple):
            # If subjectt is a tuple, take the first element
            subjectt = subjectt[0]

        subjectss = Attendance.query.filter(
            Attendance.year == year,
            Attendance.branch == branch,
            Attendance.semester == semester,
            Attendance.class_type == classtype,
            Attendance.subject == subjectt,
            Attendance.presentees.contains(student_roll_last_2_digits)
        )

        count_rows = subjectss.with_entities(func.count()).scalar()
        
        # Store the count for each subject in the dictionary
        subject_counts[subjectt] = count_rows

    # Print counts for each subject for the current roll number
      for subject, count in subject_counts.items():
        print(f"Total classes attended by roll number {roll_number}: {count} for subject {subject}.")

    # Calculate and print the total attendance counts for the current roll number
      
      total_counts = sum(subject_counts.values())
    
     # Store the attendance data for the current roll number in the dictionary
      attendance_data[roll_number] = subject_counts
      tarr.append(total_counts)
      print(f"Total classes attended by roll number {roll_number}: {total_counts}\n")
    print(tarr)
    print(attendance_data)  # Print the attendance data dictionary

      
    #   x.append(total_counts)
    
    names = []

    for roll_number in roll_numbers:
         student_info = StudentInfo.query.filter_by(Student_roll=roll_number).first()
    
         if student_info:
            names.append(student_info.Student_name)

    print(names)

    # return render_template('another_template.html',names=names, year=year, branch=branch, semester=semester, classtype=classtype, roll_numbers=roll_numbers,subjectsss=cleaned_matching_subjects1,tarr=tarr,tt=total_classes1)
    return render_template('another_template.html',
                           year=year,
                           branch=branch,
                           semester=semester,
                           classtype=classtype,
                           subjectsss=cleaned_matching_subjects1,
                           roll_numbers=roll_numbers,
                           names=names,
                           tt=total_classes1,
                           tarr=tarr,
                           to=to,
                           attendance_data=attendance_data)

if __name__ == '__main__':
    app.run(debug=True)
