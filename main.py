import win32api
from flask import Flask, render_template, url_for, request, jsonify, redirect
from datetime import date

app = Flask(__name__)
import psycopg2 as sql

conn = sql.connect(
    database = "postgres", 
    user = "postgres", 
    host= 'localhost',
    password = "Gcubed38",
    port = 5432)

def get_student_info(fname, lname, year):
    cur = conn.cursor()
    cur.execute("""SELECT id FROM students
            WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    student_id = cur.fetchall()
    if id == []:
        print("Student not found")
        return "Student not found"
    student_id = str(student_id[0][0])

    cur.execute("""SELECT phone, stars FROM students
                WHERE id = %s""", (student_id))
    students = cur.fetchall()
    stphone = students[0][0]
    ststars = students[0][1]

    cur.execute("""SELECT notes, date_given, weeks_homework_not_done FROM feedback
                WHERE student_id = %s
                ORDER BY date_given ASC;""", (student_id))
    feedback = cur.fetchall()

    #this code removes trailing time (minutes seconds hours) from date
    for i in range(len(feedback)):
        feedback[i] = list(feedback[i])
        feedback[i][1] = feedback[i][1].strftime('%d-%m-%Y')

    #change date to not include time

    conn.commit()
    cur.close()

    return {'fname': fname, 'lname': lname, 'year': year, 'phone': stphone, 'stars': ststars, 'feedback': feedback}


#0x00001000 - This makes the popup appear over the browser window
#runs at app run, first thing
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/studentinfo', methods=['GET', 'POST'])
def displaystudentinfo():
    fname, lname = "", ""

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year =  request.form['yr']

    cur = conn.cursor()
    #can do a lot here. i think we run a query to get the student id and info. then use
    #that id to get the feedback info. no biggie, we did it for delete
    #yeah, remodle as above.

    cur.execute("""SELECT id FROM students
            WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    student_id = cur.fetchall()
    if id == []:
        print("Student not found")
        return 0
    student_id = str(student_id[0][0])

    cur.execute("""SELECT phone, stars FROM students
                WHERE id = %s""", (student_id))
    students = cur.fetchall()
    stphone = students[0][0]
    ststars = students[0][1]

    cur.execute("""SELECT notes, date_given, weeks_homework_not_done FROM feedback
                WHERE student_id = %s
                ORDER BY date_given ASC;""", (student_id))
    feedback = cur.fetchall()

    #this code removes trailing time (minutes seconds hours) from date
    for i in range(len(feedback)):
        feedback[i] = list(feedback[i])
        feedback[i][1] = feedback[i][1].strftime('%d-%m-%Y')

    #change date to not include time
    

    #i think we just pass feedback back, and handle it there

    conn.commit()
    cur.close()

    return {'fname': fname, 'lname': lname, 'year': year, 'phone': stphone, 'stars': ststars, 'feedback': feedback}

@app.route('/studentpage', methods=['GET', 'POST'])
def changepage():
    fname = request.args.get('fn', None)
    lname = request.args.get('ln', None)
    year = request.args.get('yr', None)

    #ignore how the names are messed up we can fix that later asdjka
    # okay so what we need to do, get student data here, pass it to the edit page and load it in the form
    # once edited, we hit a button, and the values are passed to a new function, then saved.
    #make a helper function that gets students info from the fname, lname and year. helper it will help
    #last thing to do, change the feedbackdisplay so it can be edited
    #It makes sense to only be able to edit a week at a time, so a drop down menu that lets you sort for week is a good idea
    #that week becomes a textbox
    stuinfo = get_student_info(fname, lname, year)
    if stuinfo == "Student not found":
        print("Student not found")
        return render_template('studentnotfound.html')

    return render_template('studentpage.html', fn = stuinfo['fname'], ln = stuinfo['lname'], yr = stuinfo['year'], ph = stuinfo['phone'], st = stuinfo['stars'], fb = stuinfo['feedback'])
    # if request.method == 'POST':
    #     form = request.form
    #     fname = request.form['fname']
    #     lname = request.form['lname']
    #     print(form)
    
    #this pulls the args we attached to the url, renders them with the template

    print("This was called")
    
#this only renders template, if they go there...
@app.route('/createnewstudent')
def createnewstudent():
    return render_template('createnewstudent.html')

@app.route('/createstudent', methods=['GET', 'POST'])
def createstudent():
    # in future this should be a different page, for more info like phone and year. One button called edit students, that takes students to the edit page
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
def deletestudent():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year =  request.form['yr']
    cur = conn.cursor()
    cur.execute("""SELECT id FROM students
                WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    student_id = cur.fetchall()
    if student_id == []:
        print("Student not found")
        return 0
    student_id = student_id[0][0]
    print(student_id)
    cur.execute("""DELETE FROM feedback
                WHERE student_id = %s;""", (str(student_id)))
    cur.execute("""DELETE FROM students
                WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    conn.commit()
    cur.close()
    #this works
    return {'fname': fname, 'lname': lname, 'year': year}


@app.route("/changestudentinfo", methods=['GET', 'POST'])
def changestudentinfo():
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
    cur.execute("""SELECT id FROM students
            WHERE firstname = %s AND lastname = %s AND year = %s;""", (ogfname, oglname, ogyear))
    student_id = cur.fetchall()
    student_id = student_id[0][0]
    cur.execute("""UPDATE students
                SET firstname = %s, lastname = %s, year = %s, phone = %s, stars = %s
                WHERE id = %s;""", (fname, lname, year, phone, stars, student_id))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'phone': phone, 'stars': stars}


@app.route("/addfeedback", methods=['GET', 'POST'])
def addfeedback():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year = request.form['yr']
        feedback = request.form['fb']
        date_given = date.today()
        weeks_homework_not_done = request.form['weeks']
    cur = conn.cursor()
    cur.execute("""SELECT id FROM students
            WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    student_id = cur.fetchall()
    student_id = student_id[0][0]
    cur.execute("""INSERT INTO feedback(student_id, notes, date_given, weeks_homework_not_done)
                VALUES (%s, %s, %s, %s);""", (student_id, feedback, date_given, weeks_homework_not_done))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'notes': feedback, 'date_given': str(date_given), 'weeks_homework_not_done': weeks_homework_not_done}

@app.route("/editfeedback", methods=['GET', 'POST'])
def editfeedback():
    fname = request.args.get('fn', None)
    lname = request.args.get('ln', None)
    year = request.args.get('yr', None)

    stuinfo = get_student_info(fname, lname, year)
    if stuinfo == "Student not found":
        print("Student not found")
        return render_template('studentnotfound.html')
    
    return render_template('editfeedback.html', fn = fname, ln = lname, yr = year, fb = stuinfo['feedback'])

@app.route("/updatefeedback", methods=['GET', 'POST'])
def updatefeedback():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        year = request.form['yr']
        feedback = request.form['fb']
        week = request.form['week']
    cur = conn.cursor()
    cur.execute("""SELECT id FROM students
            WHERE firstname = %s AND lastname = %s AND year = %s;""", (fname, lname, year))
    student_id = cur.fetchall()
    if student_id == []:
        print("Student not found")
        return 0
    student_id = student_id[0][0]
    cur.execute("""UPDATE feedback
                SET notes = %s
                WHERE student_id = %s AND date_given = %s;""", (feedback, student_id, week))
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'notes': feedback, 'date_given': week}

if __name__ == '__main__':
    app.run(debug=True)
    conn.close()

# cur = conn.cursor()
    # cur.execute("""SELECT * FROM test_table;
    #         """)
    # rows = cur.fetchall()
    # for row in rows:
    #     print(row)
    # conn.commit()
    # cur.close()
    # fname =
    # lname =  