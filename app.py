from flask import Flask, render_template, request, redirect, url_for, flash, session
import urllib2
import json
import MySQLdb

app = Flask(__name__)
app.secret_key = "a"

try:
    con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
    c = con.cursor()
    c.execute("DROP TABLE IF EXISTS Users")
    c.execute("CREATE TABLE Users(User VARCHAR(50), Password VARCHAR(50), Gym VARCHAR(50))")
    c.execute("INSERT INTO Users VALUES('test1', 'test1', 'Blink Fitness')")
    c.execute("INSERT INTO Users VALUES('test2', 'test2', 'Golds Gym')")
    c.execute("INSERT INTO Users VALUES('test3', 'test3', 'NYC Recreation Center')")
    c.execute("DROP TABLE IF EXISTS Gyms")
    c.execute("CREATE TABLE Gyms(User VARCHAR(50), PlaceId VARCHAR(50), LatX DOUBLE PRECISION, LatY DOUBLE PRECISION)")
    c.execute("SELECT * FROM Users")
    print c.fetchall()
    con.commit()
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
finally:
    if con:
        con.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/browsegyms')
def browsegyms():
    return render_template("browsegyms.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/gymadminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
        with con:
            c = con.cursor()
            user = request.form['user']
            #TODO hash password
            password = request.form['password']
            c.execute("SELECT * FROM Users WHERE User=%s AND Password=%s LIMIT 1", (user, password))
            s = c.fetchone()
            if s == None:
                #TODO use flash
                flash("Credentials incorrect")
                return redirect(url_for("admin_login"))
            session['user'] = user
            return render_template("admin_loggedin.html", admin=user)
    return render_template("admin_login.html")

@app.route('/editgyms')
def edit_gyms():
    if 'user' in session:
        con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
        with con:
            c = con.cursor()
            user = session['user']
            c.execute("SELECT GYM FROM Users WHERE User=%s LIMIT 1", (user,))
            s = c.fetchone()
            print "s: " + s[0]
        return render_template("edit_gyms.html", gymName=s[0])
    else:
        flash("You have to log in before accessing this page")
        return redirect(url_for('admin_login'))

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))

@app.route('/api/getDetails', methods=['POST'])
def get_details():
    url = urllib2.urlopen(request.form['url'])
    d = json.loads(url.read())
    d = d['result']
    data = {}
    if 'website' in d:
        data['website'] = d['website']
    else:
        data['website'] = "Not available"
    if 'formatted_phone_number' in d:
        data['phone'] = d['formatted_phone_number']
    else:
        data['phone'] = "Not available"
    con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
    with con:
        c = con.cursor()
        user = session['user']
        id = request.form['id']
        c.execute("SELECT * FROM Gyms WHERE User=%s AND PlaceId=%s LIMIT 1", (user, id))
        s = c.fetchone()
        if s == None:
            data['button'] = "<button id='markerbutton' onclick='addGym()'>Add to your Gyms</button>"
        else:
            data['button'] = "<button id='markerbutton' onclick='removeGym()'>Remove from your Gyms</button>"
    return json.dumps(data)

@app.route('/api/addgym', methods=['POST'])
def add_gym():
    if request.method=='POST':
        con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
        with con:
            c = con.cursor()
            user = session['user']
            id = request.form['id']
            c.execute("SELECT * FROM Gyms WHERE User=%s AND PlaceId=%s LIMIT 1", (user, id))
            if c.fetchone()==None:
                x = request.form['x']
                y = request.form['y']
                c.execute("INSERT INTO Gyms VALUES(%s, %s, %s, %s)", (user, id, x, y) )
                return "Gym added!"
            return "Gym Already in your Gyms"
        return "Database Error"
    return "Malformed request"

@app.route('/api/removegym', methods=['POST'])
def remove_gym():
    if request.method=='POST':
        con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
        with con:
            c = con.cursor()
            user = session['user']
            place_id = request.form['placeId']
            c.execute("DELETE FROM Gyms WHERE User=%s AND PlaceId=%s", (user, place_id) )
            return "Gym deleted!"
        return "Database Error"
    return "Malformed request"

@app.route('/api/getgyms', methods=['POST'])
def get_gyms():
    con = MySQLdb.connect('127.0.0.1', 'testuser', 'test623', 'testdb')
    with con:
        c = con.cursor()
        user = session['user']
        data = []
        c.execute("SELECT PlaceId FROM Gyms WHERE User=%s", (user,))
        results = c.fetchall()
        for result in results:
            data.append(result[0]);
        return json.dumps(data)
    return "Error"

if __name__ == '__main__':
    app.debug = True
    app.run()
