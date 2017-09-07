from flask import Flask, flash, redirect, render_template, request, session
import sqlite3 as sql
from datetime import datetime


conn = sql.connect('test.db')
print "Opened database successfully";

c = conn.cursor()

conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS USER
         (
          username TEXT PRIMARY KEY,
          PASSWORD INTEGER);''')

c.execute('''CREATE TABLE IF NOT EXISTS USER1
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT ,
           log_time TIMESTAMP  );''')

c.execute('''CREATE TABLE IF NOT EXISTS user_log
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT ,
          event TEXT NOT NULL,
          time_log TIMESTAMP);''')

print "Tables created successfully"

conn.commit()
conn.close()

app = Flask(__name__)
app.secret_key = 'random string'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    with sql.connect("test.db") as db:
        cur = db.cursor()
        if request.method == 'POST':
            nm = request.form['username']
            cur.execute("SELECT * FROM USER WHERE username ='"+nm+"';")
            nn = cur.fetchone()
            if nn == None :
                if (request.form['password1']) == (request.form['password2']):
                    return render_template('add.html')
                else:
                    error = "Passwords donot match"
            else:
                    error = ('Username already exists!Try Again!!')
        cur.close()
    db.close()

    return render_template('signup.html', error= error)

@app.route('/add', methods=['GET', 'POST'])
def add():
        error = None

        if request.method == 'POST':
            with sql.connect("test.db") as con:
                cur = con.cursor()

            try:
                name = request.form['username']
                password = request.form['password1']


                cur.execute("INSERT INTO USER (username,password)VALUES(?, ?)",(name,password) )
                con.commit()
                msg = "Record successfully added"
                cur.close()

            except:
                    con.rollback()
                    msg = "error in insert operation"
                    con.close()

            finally:
                   return render_template("action.html", msg=msg)


@app.route('/user_list')
def user_list():
    con = sql.connect("test.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from USER")

    rows = cur.fetchall();
    return render_template("user_list.html", rows=rows)


@app.route('/login', methods=['GET', 'POST'])

def login():
    error = None
    with sql.connect("test.db") as db:
        cur = db.cursor()
        if request.method == 'POST':
            nm = request.form['username']
            cur.execute("SELECT * FROM USER WHERE username ='"+nm+"';")
            nn = cur.fetchone()
            if nn == None :
                error = 'Invalid Username , try again or signup'
            else:
                if str(nn[0]) == nm:
                    pas = request.form['password']
                    cur.execute("SELECT password FROM USER WHERE username='" + nm + "';")
                    ck = cur.fetchone()
                    if str(ck[0]) == pas:
                        session['username'] = request.form['username']
                        print (session)
                        t = datetime.now()
                        t = t.replace(microsecond=0)
                        cur.execute("INSERT INTO USER1 (username,log_time) VALUES (?,?)", (nm, t))
                        cur.execute('SELECT log_time FROM USER1 WHERE username="' + nm + '"')
                        test = cur.fetchall()
                        mylist = []
                        for t in test:
                            mylist.append(str(t[0]))
                        print "Mylogin:", mylist
                        return render_template('success.html', test=mylist)

                    else:
                        error = 'Invalid Password'



        cur.close()
    db.close()

    return render_template('login.html', error= error)


@app.route('/User_log',methods = ['POST'])
def User_log():
    error = None
    print("Entered user logs func")
    if request.method == 'POST':
        with sql.connect("test.db") as con:
            cur = con.cursor()
            nm = session['username']
            print(session)
            log = request.form['activity']
            t = datetime.now()
            t = t.replace(microsecond=0)
            cur.execute("INSERT INTO user_log (username,event,time_log) VALUES (?,?,?)", (nm,log,t))
            print ("Inserted user log")
            cur.execute('SELECT event,time_log FROM user_log WHERE username= "' + nm + '"')
            dbtest = cur.fetchall()
            dblist = []
            for t in dbtest:
                dblist.append(str(t))
            print ("DBlist", dblist)



            cur.close()
        con.close()

    return "0"

@app.route('/logout')
def logout():
    session.pop('username',None)
    return render_template('logout.html')





if __name__ == "__main__":
    app.run(debug=True)
