from flask import Flask, render_template, request, redirect, url_for, flash, session
import urllib2
import json
import MySQLdb
import math
import uuid
from random import randrange
from hidefromgithub import *
from werkzeug import secure_filename
import os
import datetime

UPLOAD_FOLDER = './static/'
ALLOWED_EXTENSIONS = set(['png', 'bmp', 'jpg'])
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


IDCOL = 0
NAMECOL = 1
USERCOL = 2
LATCOL = 3
LNGCOL = 4
ADDRESSCOL = 5
TYPECOL = 6
MISCCOL = 7
LASTUPDATECOL = 8

@app.route('/')
def index():
    admin_logged_in=False
    manager_logged_in=False
    goer_logged_in=False
    if 'admin_id' in session:
        admin_logged_in=True
    elif 'manager_id' in session:
        manager_logged_in=True
    elif 'goer_id' in session:
        goer_logged_in=True
    return render_template("index.html", adminLoggedIn=admin_logged_in, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)

@app.route('/browsegyms', methods=["GET", "POST"])
def browsegyms():
    admin_logged_in=False
    manager_logged_in=False
    goer_logged_in=False
    if 'admin_id' in session:
        admin_logged_in=True
    elif 'manager_id' in session:
        manager_logged_in=True
    elif 'goer_id' in session:
        goer_logged_in=True
    gyms = []
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        if request.method=="POST":
        #User submitted info to be searched for
            #TODO NEEDS TO BE COMPATIBLE
            c.execute("SELECT * FROM Gyms")
            gymsql = c.fetchall()
            for gymRow in gymsql:
                formDict = request.form.copy()
                match = 0
                if "price" in request.form:
                    gymPrice = gymRow[PRICECOL]
                    requestedPrice = request.form['price']
                    #user inputted price
                    if "per" in requestedPrice:
                        if requestedPrice[3:] == gymPrice[gymPrice.find(":")+1:]:
                            priceDifference = int(gymPrice[:gymPrice.find(":")]) - int(request.form[requestedPrice+'amount'])
                            if priceDifference > 0:
                                match = match + math.floor(priceDifference * .5)
                    #multiple choice price
                    else:
                        if requestedPrice.split(":")[1] == gymPrice[gymPrice.find(":")+1:]:
                            priceDifference = int(gymPrice[:gymPrice.find(":")]) - int(requestedPrice.split(":")[0])
                            if priceDifference > 0:
                                match = match + math.floor(priceDifference * .5)
                    del formDict['price']
                    print 'formdict after price'
                    print formDict
                if "from1" in request.form and "to1" in request.form:
                    hoursIndex = 1
                    fromList = []
                    toList = []
                    dayList = []
                    fromVar = request.form['from1']
                    toVar = request.form['to1']
                    dayVar = request.form['day1']
                    #del formDict['from1']
                    #del formDict['to1']
                    #del formDict['day1']
                    while fromVar and toVar and dayVar:
                        del formDict['from'+str(hoursIndex)]
                        del formDict['to'+str(hoursIndex)]
                        del formDict['day'+str(hoursIndex)]
                        if fromVar != "" and toVar != "":
                            fromList.append(fromVar)
                            toList.append(toVar)
                            dayList.append(dayVar)
                            hoursIndex = hoursIndex + 1
                            fromVar = request.form.get("from"+str(hoursIndex), None)
                            toVar = request.form.get("to"+str(hoursIndex), None)
                            dayVar = request.form.get("day"+str(hoursIndex), None)
                    match = match + analyzeHours(gymRow, dayList, fromList, toList)
                    for timeIndex in range(len(fromList)):
                        fromVar = fromList[timeIndex]
                        toVar = toList[timeIndex]
                        dayVar = dayList[timeIndex]
                        print "s: " + fromVar
                        print "t: " + toVar
                        print "d: " + dayVar
                if "gymType" in request.form:
                    print "wanted gymType: " + request.form['gymType']
                    print "actual gymType: " + gymRow[TYPECOL]
                    if request.form['gymType'] != gymRow[TYPECOL]:
                        match = match + 20
                    del formDict['gymType']
                print formDict
                #TODO: location, then finally, equipment
                if "loc" in request.form:
                    url = "https://api.foursquare.com/v2/venues/GYM_ID?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20130815".replace("CLIENT_ID", "L4UK14EMS0MCEZOVVUYX2UO5ULFHJN3EHOFVQFSW0Z1MSFSR").replace("CLIENT_SECRET", "YKJB0JRFDPPSGTHALFOEP5O1NDDATHKQ2IZ5RO2GOX452SFA")
                    print url
                    print "loc: " + request.form['loc']
                    userLoc = request.form['loc']
                    if userLoc == "otheraddress":
                        #url = https://api.foursquare.com/v2/venues/search?client_id=L4UK14EMS0MCEZOVVUYX2UO5ULFHJN3EHOFVQFSW0Z1MSFSR&client_secret=YKJB0JRFDPPSGTHALFOEP5O1NDDATHKQ2IZ5RO2GOX452SFA&v=20130815&ll=40.7426683,-73.8831344&query=gym&address=4210%2082nd%20st%20elmhurst%20ny%2011373&radius=8046.72
                        ####gets gyms near my address
                        url = url.replace("GYM_ID", "search") + "&address=" + request.form['userLoc'].replace(" ", "%20") + "&radius=" + str(float(request.form['otheraddressamount'])*1609.34) + "&ll=" + request.form['myLoc'] + "&query=gym%20fitness"
                        print "othr"
                        print url
                        jsondata = urllib2.urlopen(url)
                        foursquareGyms = json.loads(jsondata.read())['response']['venues']
                        gymWithinRadius = False
                        for foursquareGym in foursquareGyms:
                            if foursquareGym['id'] == gymRow[IDCOL]:
                                gymWithinRadius = True
                                print foursquareGym['name']
                                print foursquareGym['id']
                                print "gym in gymsql!"
                        if not gymWithinRadius:
                            #TODO select a random gym, use distance between that gym and gymRow[IDCOL]
                            if len(foursquareGyms)>0:
                                randIndex = randrange(0, len(foursquareGyms))
                                print randIndex
                            else:
                                match = match + 3
                    elif userLoc == "twoloc":
                        print "between"
                        #get ne_input and sw_input from another search, intent=match
                        ###that's not working, so plan b:
                        #####click two locations, find route between them/latlng between them
                        #address1Url = url.replace("GYM_ID", "search") + "&address=" + request.form['ad1'] + "&intent=match&query=gym" + "&ll=" + request.form['myLoc']
                        #print "blsjfoa"
                        #address2 = request.form['ad2']
                        #url = url.replace("GYM_ID", "search") + "&query=gym%20fitness&intent=browse&sw=SW_INPUT$ne=NE_INPUT"
                        #print url
                        print "Not yet, my friend"
                    else:
                        url = url.replace("GYM_ID", gymRow[IDCOL]) + "&ll=" + request.form['myLoc']
                        jsondata = urllib2.urlopen(url)
                        distance = json.loads(jsondata.read())['response']['venue']['location']['distance']/1609.34
                        if userLoc =="current":
                            userDistance = request.form['userDistance']
                        else:
                            userDistance = userLoc
                        if distance > float(userDistance):
                            match = match + (distance-float(userDistance))
                        print "num from current: " + userLoc
                        print "my address: " + request.form['myLoc']
                        print "gym address: " + str(gymRow[LATCOL]) + "," + str(gymRow[LNGCOL])
                        if distance > userLoc:
                            match = match + (userLoc-distance)
                    del formDict['loc']
                print formDict
                for equipment in formDict:
                    print equipment
                    if equipment in globalEquipmentList:
                        words = equipment.split(" ")
                        i = 0
                        while i < len(words):
                            words[i] = words[i].capitalize()
                            i = i + 1
                            capEquipment = "_".join(words)
                        c.execute("SELECT " + capEquipment + " from Gyms WHERE GymId=%s LIMIT 1", (gymRow[IDCOL],))
                        if int(c.fetchone()[0]) <= 0:
                            match = match + 3
                if match < 50:
                    hours= "<u>Monday:</u><br>" + displayHours(gymRow[MONDAYCOL]) + \
                        "<br><u>Tuesday:</u><br>" + displayHours(gymRow[TUESDAYCOL]) + \
                        "<br><u>Wednesday:</u><br>" + displayHours(gymRow[WEDNESDAYCOL]) + \
                        "<br><u>Thursday:</u><br>" + displayHours(gymRow[THURSDAYCOL]) + \
                        "<br><u>Friday:</u><br>" + displayHours(gymRow[FRIDAYCOL]) + \
                        "<br><u>Saturday:</u><br>" + displayHours(gymRow[SATURDAYCOL]) + \
                        "<br><u>Sunday:</u><br>" + displayHours(gymRow[SUNDAYCOL])
                    hours = hours.replace(": <br>", ": Closed<br>")
                    gym = {
                        "id": gymRow[IDCOL],
                        "name": gymRow[NAMECOL],
                        "lat": gymRow[LATCOL],
                        "lng": gymRow[LNGCOL],
                        "price": gymRow[PRICECOL].replace(":", " per "),
                        "hours": hours,
                        "address": gymRow[ADDRESSCOL],
                        "match": match
                        }
                    gyms.append(gym)
                print match
            showAll = False
        else:
            #User didn't search, show general listings
            c.execute("SELECT * FROM Gyms")
            results = c.fetchall()
            for result in results:
                gym = {
                    "id": result[IDCOL],
                    "name": result[NAMECOL],
                    "lat": result[LATCOL],
                    "lng": result[LNGCOL]
                    }
                gyms.append(gym)
            showAll = True
    equipmentList = ['barbells', 'basketball court', 'belay device', 'bench press', 'bumper plates', 'chalk', 'crashpads', 'dumbbells', 'elliptical', 'foam roller', 'jump ropes', 'kettlebells', 'locker room', 'medicine balls', 'stairmaster', 'olympic weightlifting platform', 'parking', 'personal trainer', 'physical therapy', 'pool', 'power rack', 'resistance bands', 'rings', 'rock climbing shoes', 'rowers', 'sauna', 'shower', 'squat rack', 'stationary bikes', 'stretching area', 'towels', 'tredmill', 'television', 'wifi', 'yoga mats', 'zumba', 'deadlift space', 'pilates', 'track']
    weightsList = ['squat rack', 'power rack', 'bench press', 'deadliift space', 'olympic weightlifting platform', 'dumbbells', 'kettlebells', 'barbells']
    enduranceList = ['tredmill', 'stairmaster', 'elliptical', 'kettlebells', 'pool', 'track', 'jump ropes', 'stationary bike']
    hygeneList = ['shower', 'locker room', 'sauna', 'towels']
    funList = ['wifi', 'television']
    servicesList = ['personal training', 'physical therapy', 'wifi', 'television', 'parking']
    gymClassList = ['yoga', 'pilates', 'zumba', 'rock climbing']
    mobilityList = ['stretching area', 'foam roller']
    equipmentList.sort()
    weightsList.sort()
    enduranceList.sort()
    hygeneList.sort()
    funList.sort()
    servicesList.sort()
    gymClassList.sort()
    mobilityList.sort()
    equipment = ""
    weights = ""
    endurance = ""
    hygene = ""
    fun = ""
    services = ""
    gymClass = ""
    mobility = ""
    #for e in globalEquipmentList:
    equipment = checkboxify(globalEquipmentList)
    #equipment = equipment + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in weightsList:
    weights = checkboxify(weightsList)
    #weights = weights + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in enduranceList:
    endurance = checkboxify(enduranceList)
    #endurance = endurance + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in hygeneList:
    hygene = checkboxify(hygeneList)
    #hygene = hygene + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in funList:
    fun = checkboxify(funList)
    #fun = fun + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in servicesList:
    services = checkboxify(servicesList)
    #services = services + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in gymClassList:
    gymClass = checkboxify(gymClassList)
    #gymClass = gymClass + '''<div class="checkbox"><label><input type="checkbox" class="equipmentcheckbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    #for e in mobilityList:
    mobility = checkboxify(mobilityList)
    #mobility = mobility + '''<div class="checkbox"><label><input type="checkbox" name="''' + e + '''">''' + capE + '''</label></div>'''
    print gyms
    return render_template("browsegyms.html", adminLoggedIn=admin_logged_in, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in, gyms=gyms, showAll=showAll, equipment=equipment, weights=weights, endurance=endurance, hygene=hygene, fun=fun, services=services, gymClass=gymClass, mobility=mobility)

def checkboxify(list):
    ans = ""
    for item in list:
        wordsList = item.split(" ")
        i = 0
        while i < len(wordsList):
            wordsList[i] = wordsList[i].capitalize()
            i = i + 1
        capitalizedItem = " ".join(wordsList)
        ans = ans + '<div class="checkbox"><label><input type="checkbox" name="' + item + '">' + capitalizedItem + '</label></div>'
    return ans

def displayHours(hours):
    if hours=="":
        return "Closed<br>"
    print 'hours:'
    print hours
    hoursList = hours.split(";")
    displayedHours = ""
    for hoursSet in hoursList:
        print "HoursSet: "
        print hoursSet
        newHoursSet = []
        for oneTime in hoursSet.split("-"):
            if int(oneTime.split(":")[0]) > 12:
                newHoursSet.append(str(int(oneTime.split(":")[0])-12) + ":" + oneTime.split(":")[1] + "pm")
            else:
                newHoursSet.append(oneTime + "am")
            newHoursSetString = "-".join(newHoursSet)
        displayedHours = displayedHours + newHoursSetString + "<br>"
    return displayedHours

def analyzeHours(gymRow, dayList, userStartList, userEndList):
    dayIndex = 0
    match = 0
    while dayIndex < len(dayList):
        day = dayList[dayIndex]
        if day=="Weekdays":
            dayList.extend(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"))
            startVar = userStartList[0]
            userStartList.extend((startVar, startVar, startVar, startVar, startVar))
            endVar = userEndList[0]
            userEndList.extend((endVar, endVar, endVar, endVar, endVar))
        elif day=="Weekends":
            dayList.extend(("Saturday", "Sunday"))
            startVar = userStartList[0]
            userStartList.extend((startVar, startVar))
            endVar = userEndList[0]
            userEndList.extend((endVar, endVar))
        else:
            userStartVar = userStartList[dayIndex]
            userEndVar = userEndList[dayIndex]
            numTimeWanted = float(userEndVar.split(":")[0]) - float(userStartVar.split(":")[0]) + (float(userEndVar.split(":")[1])/60) - (float(userStartVar.split(":")[1])/60)
            numTimeAvailable = 0
            for gymHours in gymRow[hoursColDict[day]].split(";"):
                print 'gym hours: ' + gymHours
                print 'chosen hours: ' + userStartVar + "-" + userEndVar
                if gymHours != "":
                    gymStartVar = gymHours.split("-")[0]
                    gymEndVar = gymHours.split("-")[1]
                    if userStartVar >= gymStartVar and userStartVar < gymEndVar: #opens at good time
                        if userEndVar > gymEndVar: #closes earlier than wanted
                            numTimeAvailable = numTimeAvailable + float(gymEndVar.split(":")[0]) - float(userStartVar.split(":")[0]) + (float(gymEndVar.split(":")[1])/60) - (float(userStartVar.split(":")[1])/60)
                        else: #closes at good time
                            numTimeAvailable = numTimeWanted
                    elif userStartVar < gymStartVar and userEndVar > gymStartVar: #opens later than wanted
                        if userEndVar > gymEndVar: #closes earlier than wanted
                            numTimeAvailable = numTimeAvailable + float(gymEndVar.split(":")[0]) - float(gymStartVar.split(":")[0]) + (float(gymEndVar.split(":")[1])/60) - (float(gymStartVar.split(":")[1])/60)
                        else: #closes at good time
                            numTimeAvailable = numTimeAvailable + float(userEndVar.split(":")[0]) - float(gymStartVar.split(":")[0]) + (float(userEndVar.split(":")[1])/60) - (float(gymStartVar.split(":")[1])/60)
                    print "time wanted: " + str(numTimeWanted)
                    print "time available: " + str(numTimeAvailable)
                match = match + ((numTimeWanted-numTimeAvailable)*5)
        dayIndex = dayIndex + 1
    print "match:"
    print match
    return match

def settings():
    return render_template("settings.html")

@app.route('/about')
def about():
    admin_logged_in=False
    manager_logged_in=False
    goer_logged_in=False
    if 'admin_id' in session:
        admin_logged_in=True
    elif 'manager_id' in session:
        manager_logged_in=True
    elif 'goer_id' in session:
        goer_logged_in=True
    return render_template("about.html", adminLoggedIn=admin_logged_in, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)

@app.route('/contact')
def contact():
    admin_logged_in=False
    manager_logged_in=False
    goer_logged_in=False
    if 'admin_id' in session:
        admin_logged_in=True
    elif 'manager_id' in session:
        manager_logged_in=True
    elif 'goer_id' in session:
        goer_logged_in=True
    return render_template("contact.html", adminLoggedIn=admin_logged_in, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'manager_id' in session:
        flash("You are already logged in")
        return redirect(url_for("edit_gym"))
    if 'goer_id' in session:
        flash("You are already logged in")
        return redirect(url_for("browsegyms"))
    if 'admin_id' in session:
        flash("You are already logged in")
        return redirect(url_for("browsegyms"))
    return render_template("login.html")

@app.route('/administratorlogin', methods=['GET', 'POST'])
def administrator_login():
    if request.method == 'POST':
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            user_email = request.form['email']
            password = request.form['password']
            c = con.cursor()
            c.execute("SELECT Password FROM Administrators WHERE Email=%s", (user_email,))
            result = c.fetchone()
            if result == None:
                flash("Credentials incorrect")
                return redirect(url_for("administrator_login"))
            else:
                result = result[0]
            if not validate_password(result, password):
                flash("Credentials incorrect")
                return redirect(url_for("administrator_login"))
            c.execute("SELECT UserId FROM Administrators WHERE Email=%s", (user_email,))
            user_id = c.fetchone()[0]
            session['admin_id'] = user_id
            return redirect(url_for("admin_select_gym"))
    else:
        return render_template("administrator_login.html")
        
@app.route('/adminselectgym')
def admin_select_gym():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        if 'admin_id' in session:
            taken_gyms = get_gyms()
            equipment = ""
            j = 0
            while j < len(globalEquipmentList):
                e = globalEquipmentList[j]
                words = e.split(" ")
                i = 0
                while i < len(words):
                    words[i] = words[i].capitalize()
                    i = i + 1
                capE = " ".join(words)
                undE = "_".join(words)
                equipment = equipment + str('''<div class="checkbox"><label><input onchange="endisable('%s')" type="checkbox" class="equipmentcheckbox" name=%s><input class='equipment' id='%s' name='%s' type="text" value="0" size="2" maxamount="2" disabled>%s</label></div>'''%(e, e, e, undE, capE))
                j = j + 1
            return render_template("admin_select_gym.html", equipment=equipment, takenGyms=taken_gyms)
        else:
            flash("You aren't logged in")
            return redirect(url_for("administrator_login"))

@app.route('/gymmanagerlogin', methods=['POST'])
def gym_manager_login():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user_email = request.form['email']
        password = request.form['password']
        c.execute("SELECT Password FROM GymManagers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result == None:
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        else:
            result = result[0]
        print result
        if not validate_password(result, password):
            c.execute("SELECT * FROM GymManagers")
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        c.execute("SELECT UserId FROM GymManagers WHERE Email=%s LIMIT 1", (user_email,))
        user_id = c.fetchone()[0]
        c.execute("SELECT GymId FROM Gyms WHERE UserId=%s", (user_id,))
        result = c.fetchone()
        if result != None:
            session['manager_id'] = user_id
            gym_id = result[0]
            session['gym_id'] = gym_id
            return redirect(url_for("edit_gym"))
        flash("Credentials incorrect")
        return redirect(url_for("login"))
    flash("Database Error")
    return redirect(url_for('index'))

@app.route('/gymmanagersignup', methods=['POST'])
def gym_manager_signup():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user_email = request.form['email']
        c.execute("SELECT * FROM GymManagers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result == None:
            user_id = uuid.uuid4()
            user_id = "0x" + str(user_id).replace("-", "")
            c.execute("SELECT * FROM GymManagers WHERE UserId=%s LIMIT 1", (user_id,))
            user_id_taken = c.fetchone()
            while user_id_taken:
                user_id = uuid.uuid4()
                user_id = "0x" + str(user_id).replace("-", "")
                c.execute("SELECT * FROM GymManagers WHERE UserId=%s LIMIT 1", (user_id,))
                user_id_taken = c.fetchone()
            password = create_password(request.form['password'])
            c.execute("INSERT INTO GymManagers VALUES(" + user_id + ", %s, %s)", (user_email, password,))
            c.execute("SELECT UserId FROM GymManagers WHERE Email=%s LIMIT 1", (user_email,))
            result = c.fetchone()
            if result != None:
                user_id = result[0]
                session['manager_id'] = user_id
                flash("Registration successful!")
                return redirect(url_for("select_gym"))
            flash("Sorry, there was an error")
            return redirect(url_for("login"))
        flash("Username taken")
        return redirect(url_for("login"))
    return "Error"

@app.route('/consumerlogin', methods=['POST'])
def consumer_login():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user_email = request.form['email']
        password = request.form['password']
        c.execute("SELECT Password FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result == None:
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        else:
            result = result[0]
        if not validate_password(result, password):
            c.execute("SELECT * FROM GymGoers")
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        c.execute("SELECT UserId FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result != None:
            user_id = result[0]
            session['goer_id'] = user_id
            return redirect(url_for("browsegyms"))
        flash("Credentials incorrect")
        return redirect(url_for("login"))
    flash("Database Error")
    return redirect(url_for('index'))

@app.route('/consumersignup', methods=['POST'])
def consumer_signup():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user_email = request.form['email']
        c.execute("SELECT * FROM GymManagers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result != None:
            flash("Please keep in mind that your 'Goer' and 'Manager' accounts are completely separate and have no affiliation other than your email")
        c.execute("SELECT * FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result == None:
            user_id = uuid.uuid4()
            user_id = "0x" + str(user_id).replace("-", "")
            c.execute("SELECT * FROM GymGoers WHERE UserId=%s LIMIT 1", (user_id,))
            user_id_taken = c.fetchone()
            while user_id_taken:
                user_id = uuid.uuid4()
                user_id = "0x" + str(user_id).replace("-", "")
                c.execute("SELECT * FROM GymGoers WHERE UserId=%s LIMIT 1", (user_id,))
                user_id_taken = c.fetchone()
            password = create_password(request.form['password'])
            c.execute("INSERT INTO GymGoers VALUES(" + user_id + ", %s, %s)", (user_email, password,))
            c.execute("SELECT UserId FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
            result = c.fetchone()
            if result != None:
                user_id = result[0]
                session['goer_id'] = user_id
                flash("Registration successful!")
                return redirect(url_for("browsegyms"))
            flash("Sorry, there was an error")
            return redirect(url_for("login"))
        flash("Username taken")
        return redirect(url_for("login"))
    return "Error"

def get_gyms():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        c.execute("SELECT GymId FROM Gyms")
        taken_gyms = []
        results = c.fetchall()
        for result in results:
            taken_gyms.append(result[0])
        return taken_gyms

@app.route('/selectgym', methods=['GET'])
def select_gym():
    #Select your gym after signing up as a manager
    if 'manager_id' in session:
        user = session['manager_id']
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            taken_gyms = get_gyms()
            equipment = ""
            j = 0
            while j < len(globalEquipmentList):
                e = globalEquipmentList[j]
                words = e.split(" ")
                i = 0
                while i < len(words):
                    words[i] = words[i].capitalize()
                    i = i + 1
                capE = " ".join(words)
                undE = "_".join(words)
                equipment = equipment + str('''<div class="checkbox"><label><input onchange="endisable('%s')" type="checkbox" class="equipmentcheckbox" name=%s><input id='%s' name='%s' type="text" value="0" size="2" maxamount="2" disabled>%s</label></div>'''%(e, e, e, undE, capE))
                j = j + 1
            return render_template("select_gym.html", user=user, takenGyms=taken_gyms, equipment=equipment)
        return "Error"
    return "Error"

@app.route('/editgym/<gym_id>', methods=["GET", "POST"])
@app.route('/editgym', methods=["GET", "POST"])
def edit_gym(gym_id=None):
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        manager_logged_in = False
        if 'manager_id' in session:
            manager_logged_in = True
            user_id = session['manager_id']
            c.execute("SELECT * FROM Gyms WHERE UserId=%s LIMIT 1", (user_id,))
            gym = c.fetchone()
        elif gym_id and 'goer_id' in session:
            c.execute("SELECT * FROM Gyms WHERE GymId=%s LIMIT 1", (gym_id,))
            gym = c.fetchone()
        else:
            flash("You have to log in before accessing this page")
            return redirect(url_for('login'))
        j = 0
        if gym==None:
            if manager_logged_in:
                #Manager logged in and hasn't chosen his gym yet
                return redirect(url_for("select_gym"))
            #User inputting info for an unverified gym
            #TODO check if goer_id in session
            misc = ""
            monday = ""
            tuesday = ""
            wednesday = ""
            thursday = ""
            friday = ""
            saturday = ""
            sunday = ""
            gym_imgs = ""
            hours = {}
            price_num = ""
            price_unit = "month"
            send_gym = True
            equipment = ""
        else:
            #Gym exists, send gym info from database to template
            gym_id = gym[IDCOL]
            session['gym_id'] = gym_id
            misc = gym[MISCCOL]
            c.execute("SELECT * FROM GymHours WHERE GymId=%s", (gym_id,))
            gym_hours_dict = {}
            gym_hours = c.fetchall()
            for gym_hour in gym_hours:
                if gym_hour[1] in gym_hours_dict:
                    gym_hours_dict[gym_hour[1]].append([gym_hour[2][:2] + ":" + gym_hour[2][2:], gym_hour[3][:2] + ":" + gym_hour[3][2:]])
                else:
                    gym_hours_dict[gym_hour[1]] = [[gym_hour[2][:2] + ":" + gym_hour[2][2:], gym_hour[3][:2] + ":" + gym_hour[3][2:]]]
            monday = ""
            tuesday = ""
            wednesday = ""
            thursday = ""
            friday = ""
            saturday = ""
            sunday = ""
            c.execute("SELECT * FROM GymEquipment WHERE GymId=%s", (gym_id,))
            gym_equipment = c.fetchall()
            gym_equipment_dict = {}
            for result in gym_equipment:
                gym_equipment_dict[result[1]] = result[2]
            equipment = gym_equipment_dict
            hours = gym_hours_dict
            gym_imgs = os.listdir(os.path.join(app.config["UPLOAD_FOLDER"], gym[IDCOL]))
            c.execute("SELECT * FROM GymPrices WHERE GymId=%s", (gym_id,))
            gym_prices = c.fetchall()
            gym_prices_list = []
            for gym_price in gym_prices:
                gym_prices_list.append([gym_price[1], gym_price[2]])
            send_gym = False
        return render_template("edit_gym.html", managerLoggedIn=manager_logged_in, gymId=gym_id, misc=misc, equipment=equipment, hours=hours, gymImgs=gym_imgs, gymPrices=gym_prices_list, sendGym=send_gym)

def dictionarifyHours(monday, tuesday, wednesday, thursday, friday, saturday, sunday):
    hours = {}
    if monday==tuesday==wednesday==thursday==friday:
        if monday==saturday==sunday:
            hours['Everyday'] = [x.split("-") for x in monday.split(";")]
        else:
            hours['Weekdays'] = [x.split("-") for x in monday.split(";")]
    else:
        hours['Monday'] = [x.split("-") for x in monday.split(";")]
        hours['Tuesday'] = [x.split("-") for x in tuesday.split(";")]
        hours['Wednesday'] = [x.split("-") for x in wednesday.split(";")]
        hours['Thursday'] = [x.split("-") for x in thursday.split(";")]
        hours['Friday'] = [x.split("-") for x in friday.split(";")]
        if saturday==sunday:
            if "Everyday" not in hours:
                hours['Weekends'] = [x.split("-") for x in saturday.split(";")]
        else:
            hours['Saturday'] = [x.split("-") for x in saturday.split(";")]
            hours['Sunday'] = [x.split("-") for x in sunday.split(";")]
    return hours

def allowed_file(filename):
    return '.' in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadImages', methods=['POST'])
def uploadImages():
    #TODO ALLOW USERS TO INPUT INFO
    if 'manager_id' in session and 'pic1' in request.files and 'gymId' in request.form:
        file = request.files['pic1']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            gym_dir = os.path.join(app.config["UPLOAD_FOLDER"], request.form['gymId'])
            if not os.path.exists(gym_dir):
                os.makedirs(gym_dir)
            file.save(os.path.join(gym_dir, filename))
            flash("File uploaded successfully")
        else:
            flash("File upload unsuccessful")
        return redirect(url_for("edit_gym"))
    else:
        return "Stop trying to break the site bro"

@app.route('/removeImages', methods=['POST'])
def removeImages():
    #TODO ALLOW USERS TO INPUT INFO
    if 'manager_id' in session and 'imgName' in request.form and 'gymId' in request.form:
        img_dir = os.path.join(app.config["UPLOAD_FOLDER"], request.form['gymId'], request.form['imgName'])
        if os.path.exists(img_dir):
            os.remove(img_dir)
            return "Image removal successful!"
    return "Image removal unsuccessful"

@app.route('/gym/<id>', methods=['GET', 'POST'])
def gympage(id):
    admin_logged_in=False
    manager_logged_in=False
    goer_logged_in=False
    if 'admin_id' in session:
        admin_logged_in=True
    elif 'manager_id' in session:
        manager_logged_in=True
    elif 'goer_id' in session:
        goer_logged_in=True
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        c.execute("SELECT * FROM Gyms WHERE GymId=%s LIMIT 1", (id,))
        gym = c.fetchone()
        #Get user price updates
        user_price_updates_dict = {}
        c.execute("SELECT * FROM UserGymPricesUpdates WHERE GymId=%s", (id,))
        info_available = c.fetchall()
        if info_available:
            for info in info_available:
                user_email = get_user_email(info[0])
                if user_email in user_price_updates_dict:
                    if info[4] == "":
                        user_price_updates_dict[user_email].append("$" + info[2] + " per " + info[3])
                    else:
                        user_price_updates_dict[user_email].append("$" + info[2] + " per " + info[3] + " for " + info[4])
                else:
                    if info[4] == "":
                        user_price_updates_dict[user_email] = ["$" + info[2] + " per " + info[3]]
                    else:
                        user_price_updates_dict[user_email] = ["$" + info[2] + " per " + info[3] + " for " + info[4]]
        #Get user equipment updates
        user_equipment_updates_dict = {}
        c.execute("SELECT * FROM UserGymEquipmentUpdates WHERE GymId=%s", (id,))
        info_available = c.fetchall()
        if info_available:
            for info in info_available:
                user_email = get_user_email(info[0])
                if user_email in user_equipment_updates_dict:
                    user_equipment_updates_dict[user_email].append(str(info[3]) + " " + info[2])
                else:
                    user_equipment_updates_dict[user_email] = [str(info[3]) + " " + info[2]]
        #Get user hours updates
        user_hours_updates_dict = {}
        c.execute("SELECT * FROM UserGymHoursUpdates WHERE GymId=%s", (id,))
        info_available = c.fetchall()
        if info_available:
            for info in info_available:
                user_email = get_user_email(info[0])
                if user_email in user_hours_updates_dict:
                    user_hours_updates_dict[user_email].append(info[2] + ": From " + info[3] + " to " + info[4])
                else:
                    user_hours_updates_dict[user_email] = [info[2] + ": From " + info[3] + " to " + info[4]]
        #Get comments
        user_comments_dict = {}
        c.execute("SELECT * FROM UserGymComments WHERE GymId=%s", (id,))
        info_available = c.fetchall()
        if info_available:
            for info in info_available:
                user_email = get_user_email(info[0])
                if user_email in user_comments_dict:
                    user_comments_dict[user_email].append(info[2])
                else:
                    user_comments_dict[user_email] = [info[2]]
        if not gym:
            #Gym is not verified by a manager
            url = "https://api.foursquare.com/v2/venues/GYM_ID?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20130815".replace("CLIENT_ID", "L4UK14EMS0MCEZOVVUYX2UO5ULFHJN3EHOFVQFSW0Z1MSFSR").replace("CLIENT_SECRET", "YKJB0JRFDPPSGTHALFOEP5O1NDDATHKQ2IZ5RO2GOX452SFA").replace("GYM_ID", id)
            jsondata = urllib2.urlopen(url)
            gym_name = json.loads(jsondata.read())['response']['venue']['name']
            if not (user_equipment_updates_dict or user_price_updates_dict or user_hours_updates_dict or user_comments_dict):
                #Unverified gym, no user info
                return render_template("new_gym.html", id=id, name=gym_name, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)
            else:
                #Unverified gym, user info available
                return render_template("new_gym_with_info.html", id=id, name=gym_name, equipment=user_equipment_updates_dict, prices=user_price_updates_dict, hours=user_hours_updates_dict, comments=user_comments_dict, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)
        #Gym is verified by manager
        name = gym[NAMECOL]
        prices = []
        c.execute("SELECT * FROM GymPrices WHERE GymId=%s", (id,))
        gym_prices = c.fetchall()
        gym_prices_list = []
        for gym_price in gym_prices:
            gym_prices_list.append([gym_price[1], gym_price[2]])
        misc = gym[MISCCOL]
        c.execute("SELECT * FROM GymHours WHERE GymId=%s", (id,))
        gym_hours = c.fetchall()
        gym_hours_dict = {}
        for gym_hour in gym_hours:
            if gym_hour[1] in gym_hours_dict:
                gym_hours_dict[gym_hour[1]].append([gym_hour[2][:2] + ":" + gym_hour[2][2:], gym_hour[3][:2] + ":" + gym_hour[3][2:]])
            else:
                gym_hours_dict[gym_hour[1]] = [[gym_hour[2][:2] + ":" + gym_hour[2][2:], gym_hour[3][:2] + ":" + gym_hour[3][2:]]]
        hours = gym_hours_dict
        c.execute("SELECT * FROM GymEquipment WHERE GymId=%s", (id,))
        gym_equipment = c.fetchall()
        gym_equipment_dict = {}
        for result in gym_equipment:
            gym_equipment_dict[result[1]] = result[2]
        equipment = gym_equipment_dict
        gym_imgs = os.listdir(os.path.join(app.config["UPLOAD_FOLDER"], gym[IDCOL]))
        return render_template("gym_page.html", name=name, gymPrices=gym_prices_list, misc=misc, hours=hours, gym=gym, addressCol=ADDRESSCOL, lastUpdateCol=LASTUPDATECOL, gymImgs=gym_imgs, gymId=gym[IDCOL], adminLoggedIn=admin_logged_in, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in, userPrices=user_price_updates_dict, userEquipment=user_equipment_updates_dict, userHours=user_hours_updates_dict, userComments=user_comments_dict, equipment=equipment)

def get_user_email(user_id):
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        c.execute("SELECT Email FROM GymGoers WHERE UserId=%s LIMIT 1", (user_id,))
        result = c.fetchone()
        print result
        if result:
            return result[0]
        else:
            return None

def get_user_id(user_email):
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        c.execute("SELECT UserId FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        print result
        if result:
            return result[0]
        else:
            return None

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged out")
    return redirect(url_for('index'))

@app.route('/addgym', methods=['POST'])
def add_gym():
    if request.method=='POST' and ('manager_id' in session or 'admin_id' in session):
        formDict = request.form.copy()
        #check if price, hours, type are set, and if gym chosen
        #create gym with everything set except equipment
        #loop through equipment and update each column individually
        #####check if equipment is in globalEquipmentList
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            if 'manager_id' in session:
                user_id = session['manager_id']
                next_redirect = "edit_gym"
                if 'gymId' not in request.form or 'gymName' not in request.form:
                    flash("Please select a gym")
                    return redirect(url_for("select_gym"))
                if 'gymType' not in request.form or request.form['priceValue1'] == '' or request.form['to1'] == '' or request.form['from1'] == '':
                    flash("Please fill out the required fields")
                    return redirect(url_for("select_gym"))
            elif 'admin_id' in session:
                user_id = session['admin_id']
                next_redirect = "select_gym"
                if 'gymId' not in request.form or 'gymName' not in request.form:
                    flash("Please select a gym")
                    return redirect(url_for("admin_select_gym"))
                if 'gymType' not in request.form or request.form['price'] == '' or request.form['to1'] == '' or request.form['from1'] == '':
                    flash("Please fill out the required fields")
                    return redirect(url_for("admin_select_gym"))
            gym_id = request.form['gymId']
            gym_name = request.form['gymName']
            gym_lat = request.form['gymLat']
            gym_lng = request.form['gymLng']
            gym_type = request.form['gymType']
            gym_address = request.form['gymAddress']
            del formDict['gymId']
            del formDict['gymName']
            del formDict['gymLat']
            del formDict['gymLng']
            del formDict['gymType']
            del formDict['gymAddress']
            #parse through hours- same as /browsegyms
            #fromList = []
            #toList = []
            #dayList = []
            #gymPrice = request.form['priceValue1'] + ":" + request.form['priceUnit1']
            pricesIndex = 1
            gymPriceValue = request.form['priceValue1']
            gymPriceUnit = request.form['priceUnit1']
            while gymPriceValue and gymPriceUnit:
                del formDict['priceValue'+str(pricesIndex)]
                del formDict['priceUnit'+str(pricesIndex)]
                if gymPriceValue != "":
                    c.execute("INSERT INTO GymPrices VALUES (%s, %s, %s)", (gym_id, gymPriceValue, gymPriceUnit))
                    pricesIndex = pricesIndex + 1
                    gymPriceValue = request.form.get("priceValue"+str(pricesIndex), None)
                    gymPriceUnit = request.form.get("priceUnit"+str(pricesIndex), None)
            hoursIndex = 1
            fromVar = request.form['from1']
            toVar = request.form['to1']
            dayVar = request.form['day1']
            hoursDict = {}
            while fromVar and toVar and dayVar:
                del formDict['from'+str(hoursIndex)]
                del formDict['to'+str(hoursIndex)]
                del formDict['day'+str(hoursIndex)]
                #TODO CHECK IF VALUES ENTERED ARE VALID--NO INTERSECTING HOURS
                if fromVar != "" and toVar != "":
                    #TODO UNDO REPLACE :, INSTEAD CHANGE LIMIT IN RESET
                    #ACTUALLY, IT'LL SAVE MEMORY TO STORE WITHOUT IT
                    #IDK
                    c.execute("INSERT INTO GymHours VALUES(%s, %s, %s, %s)", (gym_id, dayVar, fromVar.replace(":", ""), toVar.replace(":", "")))
                    hoursIndex = hoursIndex + 1
                    fromVar = request.form.get("from"+str(hoursIndex), None)
                    toVar = request.form.get("to"+str(hoursIndex), None)
                    dayVar = request.form.get("day"+str(hoursIndex), None)
            #misc = request.form['misc']
            misc = ''
            timeNow = datetime.datetime.now().ctime() + " by Gym Manager"
            c.execute("SELECT * FROM Gyms WHERE UserId=%s AND GymId=%s LIMIT 1", (user_id, gym_id))
            if c.fetchone()==None:
                c.execute("INSERT INTO Gyms VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (gym_id, gym_name, user_id, gym_lat, gym_lng, gym_address, gym_type, misc, timeNow))
                gym_dir = os.path.join(app.config["UPLOAD_FOLDER"], gym_id)
                if not os.path.exists(gym_dir):
                    os.makedirs(gym_dir)
                flash("Gym added!")
                return redirect(url_for(next_redirect))
            return "Gym Already in your Gyms"
        return "Database Error"
    return "Malformed request"

@app.route('/api/getgyminfo', methods=['POST'])
def get_gym_info():
    #TODO NEEDS TO BE COMPATIBLE
    if 'gymId' in request.form:
        gym_id = request.form['gymId']
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            c.execute("SELECT * FROM Gyms WHERE GymId=%s LIMIT 1", (gym_id,))
            result = c.fetchone()
            c.execute("SELECT GymId FROM Gyms")
            results = c.fetchall()
            if result != None:
                ans = {'equipment': [i for i in result[EQUIPMENTSTARTCOL:]],
                       'id': result[IDCOL],
                       'price': result[PRICECOL],
                       'type': result[TYPECOL],
                       'hours': dictionarifyHours(result[MONDAYCOL], result[TUESDAYCOL], result[WEDNESDAYCOL], result[THURSDAYCOL], result[FRIDAYCOL], result[SATURDAYCOL], result[SUNDAYCOL]),
                       'requirements': result[REQCOL],
                       'misc': result[MISCCOL],
                       'images': 'TODO'
                    }
                return json.dumps(ans)
    return 'None'

@app.route('/api/removegym', methods=['POST'])
def remove_gym():
    if request.method=='POST':
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            user = session['manager_id']
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
        #TODO check if manager_id and gym_id in session
        manager_logged_in = False
        goer_logged_in = False
        if 'manager_id' in session:
            user_id = session['manager_id']
            gym_id = session['gym_id']
            manager_logged_in = True
        elif 'goer_id' in session:
            user_id = session['goer_id']
            goer_logged_in = True
        infotype = request.form['type']
        gym_id = request.form['gymId']
        if infotype != "Equipment" and infotype != "Hours" and infotype != "Misc" and infotype != "Price":
            return "bruh stop screwing with the system"
        if infotype == "Equipment":
            equipment = json.loads(request.form['text'])
            c.execute("DELETE FROM GymEquipment")
            if manager_logged_in:
                for lift in equipment:
                    print 'lift: ' + lift
                    print equipment[lift]
                    c.execute("INSERT INTO GymEquipment VALUES(%s, %s, %s)", (gym_id, lift, equipment[lift]))
            elif goer_logged_in:
                #TODO NEEDS TO BE COMPATIBLE
                c.execute("SELECT * FROM UserGymUpdates WHERE UserId=%s AND GymId=%s LIMIT 1", (user_id, gym_id))
                if c.fetchone() == None:
                    #user didnt update yet
                    c.execute("SELECT * FROM Gyms WHERE GymId=%s", (gym_id,))
                    result = c.fetchall()
                    if not result:
                        listresult = [request.form['gymId'], request.form['gymName'], user_id, request.form['lat'], request.form['lng'], request.form['address'], '', '', '', '', '', '', '', '', '', '', '', '']
                        for equipment in globalEquipmentList:
                            listresult.append(0)
                        for gym_class in globalClassesList:
                            listresult.append(0)
                        print "list result:"
                        print listresult
                        tupleresult = tuple(listresult)
                    else:
                        listresult = list(result[0])
                        listresult[USERCOL] = user_id
                        tupleresult = tuple(listresult)
                    updateRow = "INSERT INTO UserGymUpdates VALUES("
                    for item in tupleresult:
                        updateRow = updateRow + "%s, "
                    updateRow = updateRow[:-2] + ")"
                    print updateRow
                    c.execute(updateRow, tupleresult)
                    return "Thank you!"
                #TODO CHECK IF LIFT IS IN EQUIPMENT
                for lift in equipment:
                    print 'lift: ' + lift
                    print 'amaount: ' + equipment[lift]
                    #print gym_id
                    c.execute("UPDATE UserGymUpdates SET " + lift + "=%s WHERE UserId=%s AND GymId=%s", (equipment[lift], user_id, gym_id))
                    c.execute("DELETE FROM UserGymVotes WHERE UpdaterId=%s AND GymId=%s", (user_id, gym_id))
            con.commit()
            if manager_logged_in:
                update_time(gym_id)
                return "Update successful!"
            elif goer_logged_in:
                return "Thank you for your input!"
        #TODO LET USER UPDATE HOURS
        elif infotype == "Hours":
            hours = json.loads(request.form['text'])
            hoursIndex = 1
            fromVar = hours['from1']
            toVar = hours['to1']
            dayVar = hours['day1']
            hoursDict = {}
            while fromVar and toVar and dayVar and dayVar != "":
                c.execute("DELETE FROM GymHours WHERE GymId=%s", (gym_id,))
                c.execute("INSERT INTO GymHours VALUES(%s, %s, %s, %s)", (gym_id, dayVar, fromVar.replace(":", ""), toVar.replace(":", "")))
                hoursIndex = hoursIndex + 1
                fromVar = hours.get("from"+str(hoursIndex), None)
                toVar = hours.get("to"+str(hoursIndex), None)
                dayVar = hours.get("day"+str(hoursIndex), None)
            con.commit()
            update_time(gym_id)
            return "Update Successful!"
        elif infotype == "Price":
            #TODO FINISH
            if manager_logged_in:
                print 'hello'
            elif goer_logged_in:
                user_price = json.loads(request.form['text'])
                pricesIndex = 1
                gymPriceValue = request.form['priceValue1']
                gymPriceUnit = request.form['priceUnit1']
                while gymPriceValue and gymPriceUnit:
                    del formDict['priceValue'+str(pricesIndex)]
                    del formDict['priceUnit'+str(pricesIndex)]
                    if gymPriceValue != "":
                        c.execute("INSERT INTO UserGymUpdates VALUES (" + user_id + "%s, 'Price', %s)", (gym_id, gymPriceValue, gymPriceUnit))
                        pricesIndex = pricesIndex + 1
                        gymPriceValue = request.form.get("priceValue"+str(pricesIndex), None)
                        gymPriceUnit = request.form.get("priceUnit"+str(pricesIndex), None)
            return 'hi'
        else:
            info = request.form['text']
            c.execute("UPDATE Gyms SET Misc=%s WHERE UserId=%s AND GymId=%s", (info.replace('\\"', '&#34;'), user_id, gym_id))
            con.commit()
            update_time(gym_id)
            return "Update successful!"

def update_time(gym_id):
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        #Change LastUpdate
        newUpdateTime = datetime.datetime.now().ctime()
        c.execute("UPDATE Gyms SET LastUpdate=%s WHERE GymId=%s", (newUpdateTime, gym_id))
        con.commit()

@app.route('/api/voteuserchange', methods=['POST'])
def vote_user_change():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        if 'gym_id' in request.form and 'user_email' in request.form and 'vote' in request.form and 'goer_id' in session:
            gym_id = request.form['gym_id']
            updater_id = get_user_id(request.form['user_email'])
            voter_id = session['goer_id']
            if updater_id == voter_id:
                return "You can't vote for your own change"
            c.execute("SELECT Vote FROM UserGymVotes WHERE GymId=%s AND UpdaterId=%s AND VoterId=%s LIMIT 1", (gym_id, updater_id, voter_id))
            result = c.fetchone()
            if result != None:
                #User voted on change already, update vote
                if int(result[0]) == int(request.form['vote']) and int(result[0]) == 1:
                    return "You already voted in favor of this change"
                if int(result[0]) == int(request.form['vote']) and int(result[0]) == -1:
                    return "You already voted against this change"
                if int(request.form['vote']) == 1:
                    c.execute("UPDATE UserGymVotes SET Vote=1 WHERE GymId=%s AND UpdaterId=%s AND VoterId=%s", (gym_id, updater_id, voter_id))
                elif int(request.form['vote']) == -1:
                    c.execute("UPDATE UserGymVotes SET Vote=-1 WHERE GymId=%s AND UpdaterId=%s AND VoterId=%s", (gym_id, updater_id, voter_id))
                else:
                    return "Error"
                return "Your vote has been changed!"
            #User didn't vote on change yet
            if request.form['vote'] == "1":
                c.execute("INSERT INTO UserGymVotes VALUES(%s, %s, %s, 1)", (gym_id, updater_id, voter_id))
                return "Thank you!"
            elif request.form['vote'] == "-1":
                c.execute("INSERT INTO UserGymVotes VALUES(%s, %s, %s, -1)", (gym_id, updater_id, voter_id))
                return "Thank you!"
            return "Error"
        return "Error"

@app.route('/api/report', methods=['POST'])
def report():
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        user = session['manager_id']
        c.execute("INSERT INTO Reports VALUES(%s, %s)", (user, id))
        return "Report successful"

if __name__ == '__main__':
    app.debug = True
    app.run()
