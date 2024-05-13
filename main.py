from flask import Flask, render_template, url_for, request, jsonify, redirect, send_from_directory
from datetime import date

app = Flask(__name__, static_url_path='/static')
import psycopg2 as sql

conn = sql.connect(
    database = "postgres", 
    user = "postgres", 
    host = 'localhost',
    password = "password",
    port = 5432)

# FUNCTIONS
def get_student_id(fname, lname, year):
    cur = conn.cursor()
    cur.execute("""SELECT id FROM students
            WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    student_id = cur.fetchall()
    if student_id == []:
        raise Exception("Student not found")
    student_id = student_id[0][0]
    cur.close()
    return student_id

def get_student_info(fname, lname, year):
    cur = conn.cursor()
    student_id = str(get_student_id(fname, lname, year))

    cur.execute("""SELECT phone, stars FROM students
                WHERE id = %s""", (student_id))
    students = cur.fetchall()
    stphone = students[0][0]
    ststars = students[0][1]

    cur.execute("""SELECT notes, date_given, weeks_homework_not_done FROM feedback
                WHERE student_id = %s
                ORDER BY date_given ASC;""", (student_id))
    feedback = cur.fetchall()

    #Removes trailing time (minutes seconds hours) from date
    for i in range(len(feedback)):
        feedback[i] = list(feedback[i])
        feedback[i][1] = feedback[i][1].strftime('%d-%m-%Y')
    conn.commit()
    cur.close()

    return {'id': student_id, 'fname': fname, 'lname': lname, 'year': year, 'phone': stphone, 'stars': ststars, 'feedback': feedback}

# PAGES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/studentpage', methods=['GET', 'POST'])
def changePage():
    fname = request.args.get('fn', None)
    lname = request.args.get('ln', None)
    year = request.args.get('yr', None)

    stuinfo = get_student_info(fname, lname, year)
    if stuinfo == "Student not found":
        raise Exception("Student not found")

    return render_template('studentpage.html', fn = stuinfo['fname'], ln = stuinfo['lname'], yr = stuinfo['year'], ph = stuinfo['phone'], st = stuinfo['stars'], fb = stuinfo['feedback'])

@app.route('/createnewstudent')
def createNewStudent():
    return render_template('createnewstudent.html')

@app.route("/editfeedback", methods=['GET', 'POST'])
def editFeedback():
    fname = request.args.get('fn', None)
    lname = request.args.get('ln', None)
    year = request.args.get('yr', None)

    stuinfo = get_student_info(fname, lname, year)
    if stuinfo == "Student not found":
        raise Exception("Student not found")
    
    return render_template('editfeedback.html', fn = fname, ln = lname, yr = year, fb = stuinfo['feedback'])

# STATIC ROUTES, CSS / STYLES
@app.route('/styles/<path:path>', methods=['GET', 'POST'])
def sendReport(path):
    return send_from_directory('styles', path)

# CALLED ROUTES
@app.route('/studentinfo', methods=['GET', 'POST'])
def displayStudentInfo():
    fname, lname = "", ""

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year =  request.form['yr']
    stuinfo = get_student_info(fname, lname, year)
    stphone = stuinfo['phone']
    ststars = stuinfo['stars']
    feedback = stuinfo['feedback']

    return {'fname': fname, 'lname': lname, 'year': year, 'phone': stphone, 'stars': ststars, 'feedback': feedback}

@app.route('/createstudent', methods=['GET', 'POST'])
def createStudent():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year =  request.form['yr']
        phone = request.form['ph']
        stars = request.form['st']
    cur = conn.cursor()
    cur.execute("""INSERT INTO students(firstname, lastname, year, phone, stars)
                VALUES (%s, %s, %s, %s, %s);""", (fname, lname, year, phone, stars))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'phone': phone, 'stars': stars}

@app.route('/deletestudent', methods=['GET', 'POST'])
def deleteStudent():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year =  request.form['yr']
    student_id = get_student_id(fname, lname, year)
    cur = conn.cursor()
    cur.execute("""DELETE FROM feedback
                WHERE student_id = %s;""", (str(student_id)))
    cur.execute("""DELETE FROM students
                WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year}


@app.route("/changestudentinfo", methods=['GET', 'POST'])
def changeStudentInfo():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year = request.form['yr']
        phone = request.form['ph']
        stars = request.form['st']
        ogfname = request.form['ogfn']
        oglname = request.form['ogln']
        ogyear = request.form['ogyear']
    cur = conn.cursor()
    student_id = get_student_id(ogfname, oglname, ogyear)
    cur.execute("""UPDATE students
                SET firstname = %s, lastname = %s, year = %s, phone = %s, stars = %s
                WHERE id = %s;""", (fname, lname, year, phone, stars, student_id))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'phone': phone, 'stars': stars}

@app.route("/addfeedback", methods=['GET', 'POST'])
def addFeedback():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year = request.form['yr']
        feedback = request.form['fb']
        date_given = date.today()
        weeks_homework_not_done = request.form['weeks']
    cur = conn.cursor()
    student_id = get_student_id(fname, lname, year)
    cur.execute("""INSERT INTO feedback(student_id, notes, date_given, weeks_homework_not_done)
                VALUES (%s, %s, %s, %s);""", (student_id, feedback, date_given, weeks_homework_not_done))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'notes': feedback, 'date_given': str(date_given), 'weeks_homework_not_done': weeks_homework_not_done}

@app.route("/updatefeedback", methods=['GET', 'POST'])
def updateFeedback():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year = request.form['yr']
        feedback = request.form['fb']
        week = request.form['week']
    cur = conn.cursor()
    student_id = get_student_id(fname, lname, year)
    cur.execute("""UPDATE feedback
                SET notes = %s
                WHERE student_id = %s AND date_given = %s;""", (feedback, student_id, week))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'notes': feedback, 'date_given': week}


@app.route("/deletefeedback", methods=['GET', 'POST'])
def deleteFeedback():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year = request.form['yr']
        week = request.form['week']
    cur = conn.cursor()
    student_id = get_student_id(fname, lname, year)
    cur.execute("""DELETE FROM feedback
                WHERE student_id = %s AND date_given = %s;""", (student_id, week))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'date_given': week}

if __name__ == '__main__':
    app.run(debug=True)
    conn.close()
