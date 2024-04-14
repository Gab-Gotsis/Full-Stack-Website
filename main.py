import win32api
from flask import Flask, render_template, url_for, request, jsonify, redirect

app = Flask(__name__)
import psycopg2 as sql

conn = sql.connect(
    database = "postgres", 
    user = "postgres", 
    host= 'localhost',
    password = "Gcubed38",
    port = 5432)


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

    
    return {'fname': fname, 'lname': lname, 'year': year}

@app.route('/studentpage', methods=['GET', 'POST'])
def changepage():
    fname = request.args.get('fn', None)
    lname = request.args.get('ln', None)

    return render_template('studentpage.html', fn = fname, ln = lname)
    # if request.method == 'POST':
    #     form = request.form
    #     fname = request.form['fname']
    #     lname = request.form['lname']
    #     print(form)
    
    #this pulls the args we attached to the url, renders them with the template

    print("This was called")
    
#this only renders template, if they go there...
@app.route('/editstudents')
def editstudents():
    print("new template")
    return render_template('editstudents.html')

@app.route('/createstudent', methods=['GET', 'POST'])
def createstudent():
    print("This was called, me, the good one")
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
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.commit()
    cur.close()
    return {'fname': fname, 'lname': lname, 'year': year, 'phone': phone, 'stars': stars}


@app.route('/test2')
def test2():
    cur = conn.cursor()
    cur.execute("""INSERT INTO test_table(sometext)
                VALUES ('This is a test');
                """)
    conn.commit()
    cur.close()
    win32api.MessageBox(0, 'Hello, World!', 'Running a pythonscript via javascript on button hit!', 0x00001000)
    return render_template('index.html')
#can pass in a variable to the route, and then use that variable in the template, but use this otherwise

@app.route('/test3', methods=['GET', 'POST'])
def test3():
    if request.method == 'POST':
        form = request.form
        print(form)
    
    print("This works")
    return render_template('index.html')


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