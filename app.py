from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import urllib2
import json
import MySQLdb
import math

app = Flask(__name__)
app.secret_key = "a"

try:
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    c = con.cursor()
    c.execute("DROP TABLE IF EXISTS Gyms")
    c.execute("DROP TABLE IF EXISTS Users")
    c.execute("CREATE TABLE Users(User VARCHAR(50), Password VARCHAR(50), PRIMARY KEY (User))")
    c.execute("CREATE TABLE Gyms(GymId VARCHAR(50), GymName VARCHAR(50), User VARCHAR(50), LatX DOUBLE PRECISION, LatY DOUBLE PRECISION, GymType VARCHAR(50), Squat TINYINT, Bench TINYINT, Cardio TINYINT, Pool TINYINT, Price VARCHAR(20), Requirements VARCHAR(1000), Misc VARCHAR(1000), PRIMARY KEY (GymId), FOREIGN KEY (User) REFERENCES Users(User) ON DELETE CASCADE)")
    print c.execute("INSERT INTO Users VALUES('a@a.com', 'asdfa')")
    print c.execute("INSERT INTO Gyms VALUES('541cb2a8498e9895756f50f5', 'Blink Fitness', 'a@a.com', 40.747241, -73.887637, 'rec', 0, 3, 6, 1, '50:month', 'age:18+', 'free pizza every Monday')")
    con.commit()
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
finally:
    if con:
        con.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/browsegyms', methods=["GET", "POST"])
def browsegyms():
    gyms = []
    if request.method=="POST":
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            c.execute("SELECT * FROM Gyms")
            gymsql = c.fetchall()
            for gymRow in gymsql:
                match = 0
                if "squat" in request.form:
                    if gymRow[6] < 1:
                        match = match + 15
                if "bench" in request.form:
                    if gymRow[7] < 1:
                        match = match + 15
                if "cardio" in request.form:
                    if gymRow[8] < 1:
                        match = match + 15
                if "pool" in request.form:
                    if gymRow[9] < 1:
                        match = match + 15
                if "price" in request.form:
                    gymPrice = gymRow[10]
                    requestedPrice = request.form['price']
                    if "per" in requestedPrice:
                        if requestedPrice == gymPrice[gymPrice.find(":"):]:
                            priceDifference = int(gymPrice[:gymPrice.find(":")]) - int(request.form[requestedPrice+'amount'])
                            if priceDifference > 0:
                                match = match + math.floor(priceDifference * .5)
                    else:
                        if requestedPrice.split(":")[1] == gymPrice[gymPrice.find(":")+1:]:
                            priceDifference = int(gymPrice[:gymPrice.find(":")]) - int(requestedPrice.split(":")[0])
                            if priceDifference > 0:
                                match = match + math.floor(priceDifference * .5)
                if match < 10:
                    gym = {
                        "id": gymRow[0],
                        "name": gymRow[1],
                        "lat": gymRow[3],
                        "lng": gymRow[4],
                        "price": gymRow[10].replace(":", " per "),
                        "hours": "N/A",
                        "address": "N/A",
                        "match": match
                        }
                    gyms.append(gym)
            showAll = "False"
    else:
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            c.execute("SELECT * FROM Gyms")
            results = c.fetchall()
            for result in results:
                gym = {
                    "id": result[0],
                    "name": result[1],
                    "lat": result[3],
                    "lng": result[4]
                    }
                gyms.append(gym)
            showAll = "True"
    return render_template("browsegyms.html", gyms=gyms, showAll=showAll)

def settings():
    return render_template("settings.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

#TODO wrapper to redirect to edit_gym if logged in
@app.route('/gymadminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            user = request.form['email']
            #TODO hash password
            password = request.form['password']
            c.execute("SELECT * FROM Users WHERE User=%s AND Password=%s LIMIT 1", (user, password))
            s = c.fetchone()
            if s == None:
                flash("Credentials incorrect")
                return redirect(url_for("admin_login"))
            session['user'] = user
            return redirect(url_for("edit_gym"))
    return render_template("admin_login.html")

@app.route('/signup', methods=['POST'])
def signup():
    if request.method=="POST":
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            user = request.form['email']
            session['user'] = user
            #TODO hash password
            c.execute("SELECT * FROM Users WHERE User=%s LIMIT 1", (user,))
            s = c.fetchone()
            if s == None:
                password = request.form['password']
                c.execute("INSERT INTO Users VALUES(%s, %s)", (user, password))
                flash("Registration successful!")
                return redirect(url_for("select_gym"))
            flash("Username taken")
            return redirect(url_for("admin_login"))
    return "Error"

@app.route('/selectgym', methods=['GET'])
def select_gym():
    if 'user' in session:
        user = session['user']
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            c.execute("SELECT GymId FROM Gyms")
            taken_gyms = []
            results = c.fetchall()
            for result in results:
                taken_gyms.append(result[0])
            return render_template("select_gym.html", user=user, takenGyms=taken_gyms)
        return "Error"
    return "Error"

@app.route('/editgym', methods=["GET", "POST"])
def edit_gym():
    if 'user' in session:
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            user = session['user']
            c.execute("SELECT * FROM Gyms WHERE User=%s LIMIT 1", (user,))
            gym = c.fetchone()
            gym_id = gym[0]
            squat = gym[6]
            bench = gym[7]
            cardio = gym[8]
            pool = gym[9]
            requirements = gym[11]
            misc = gym[12]
            return render_template("edit_gym.html", gym_id=gym_id, equipment={'squat':(squat, "Squat Rack(s)"), 'bench':(bench, "Bench(es)"), 'cardio':(cardio, "Cardio Machine(s)"), 'pool':(pool, "Pool(s)")}, squat=squat, bench=bench, cardio=cardio, pool=pool, requirements=requirements, misc=misc)
    else:
        flash("You have to log in before accessing this page")
        return redirect(url_for('admin_login'))

@app.route('/gym/<id>')
def gympage(id):
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        c.execute("SELECT * FROM Gyms WHERE GymId=%s LIMIT 1", (id,))
        gym = c.fetchone()
        name = gym[1]
        price = gym[10].replace(":", " per ")
        requirements = gym[11]
        misc = gym[12]
        equipment = {"squat": (gym[6], "Squat Rack(s)"),
                "bench": (gym[7], "Bench(es)"),
                "cardio": (gym[8], "Cardio Machine(s)"),
                "pool": (gym[9], "Pool(s)")
                }
    return render_template("gym_page.html", name=name, price=price, requirements=requirements, misc=misc, equipment=equipment)

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))

@app.route('/addgym', methods=['POST'])
def add_gym():
    if request.method=='POST':
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            user = session['user']
            if 'gymId' not in request.form or 'gymName' not in request.form:
                flash("Please select a gym")
                return redirect(url_for("select_gym"))
            gymId = request.form['gymId']
            gymName = request.form['gymName']
            gymLat = request.form['gymLat']
            gymLng = request.form['gymLng']
            c.execute("SELECT * FROM Gyms WHERE User=%s AND GymId=%s LIMIT 1", (user, gymId))
            if c.fetchone()==None:
                c.execute("INSERT INTO Gyms VALUES(%s, %s, %s, %s, %s, 'N/A', 0, 0, 0, 0, '', '', '')", (gymId, gymName, user, gymLat, gymLng) )
                flash("Gym added!")
                return redirect(url_for("edit_gym"))
            return "Gym Already in your Gyms"
        return "Database Error"
    return "Malformed request"

@app.route('/api/removegym', methods=['POST'])
def remove_gym():
    if request.method=='POST':
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            user = session['user']
            place_id = request.form['placeId']
            c.execute("DELETE FROM Gyms WHERE User=%s AND GymId=%s", (user, place_id) )
            return "Gym deleted!"
        return "Database Error"
    return "Malformed request"


@app.route('/api/updateinfo', methods=['POST'])
def update_info():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user = session['user']
        infotype = request.form['type']
        gym_id = request.form['gymId']
        if infotype != "Equipment" and infotype != "Requirements" and infotype != "Misc":
            return "bruh stop screwing with the system"
        if infotype == "Equipment":
            info = json.loads(request.form['text'])
            for lift in info:
                c.execute("UPDATE Gyms SET " + lift + "=%s WHERE User=%s AND GymId=%s", (info[lift], user, gym_id))
            return "Update successful!"
        info = request.form['text']
        c.execute("UPDATE Gyms SET " + infotype + "=%s WHERE User=%s AND GymId=%s", (info, user, gym_id))
        return "Update successful!"

@app.route('/api/report', methods=['POST'])
def report():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user = session['user']
        c.execute("INSERT INTO Reports VALUES(%s, %s)", (user, id))
        return "Report successful"

if __name__ == '__main__':
    app.debug = True
    app.run()
