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
#import re

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
PRICECOL = 7
MONDAYCOL = 8
TUESDAYCOL = 9
WEDNESDAYCOL = 10
THURSDAYCOL = 11
FRIDAYCOL = 12
SATURDAYCOL = 13
SUNDAYCOL = 14
REQCOL = 15
MISCCOL = 16
LASTUPDATECOL = 17
EQUIPMENTSTARTCOL = 18
SQUATCOL = 18
BENCHCOL = 19
CARDIOCOL = 20
POOLCOL = 21
hoursColDict = {
    "Monday": MONDAYCOL,
    "Tuesday": TUESDAYCOL,
    "Wednesday": WEDNESDAYCOL,
    "Thursday": THURSDAYCOL,
    "Friday": FRIDAYCOL,
    "Saturday": SATURDAYCOL,
    "Sunday": SUNDAYCOL
}
globalEquipmentList = ['barbells', 'basketball court', 'belay device', 'bench press', 'bumper plates', 'chalk', 'crashpads', 'dumbbells', 'elliptical', 'foam roller', 'jump ropes', 'kettlebells', 'locker room', 'medicine balls', 'stairmaster', 'olympic weightlifting platform', 'parking', 'personal trainer', 'physical therapy', 'pool', 'power rack', 'resistance bands', 'rings', 'rock climbing shoes', 'rowers', 'sauna', 'shower', 'squat rack', 'stationary bikes', 'stretching area', 'towels', 'tredmill', 'television', 'wifi', 'yoga mats', 'deadlift space', 'track']
globalClassesList = ['yoga', 'pilates', 'zumba', 'rock climbing']
globalEquipmentList.sort()
globalClassesList.sort()
UPVOTECOL = EQUIPMENTSTARTCOL + len(globalEquipmentList) + len(globalClassesList)
DOWNVOTECOL = UPVOTECOL + 1

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
    if request.method=="POST":
        print request.form
        for x in request.form:
            print x + ": " + request.form[x]
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            c.execute("SELECT * FROM Gyms")
            gymsql = c.fetchall()
            for gymRow in gymsql:
                formDict = request.form.copy()
                print "formdict: "
                print formDict
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
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
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
    #equipmentList = ['abmat', 'barbells', 'basketball court', 'belay device', 'bench press', 'bumper plates', 'carabeners', 'chalk', 'climbing helmet', 'climbing rope', 'crashpads', 'dumbbells', 'elliptical', 'foam roller', 'harness', 'jump ropes', 'kettlebells', 'locker room', 'medicine balls', 'stairmaster', 'olympic weightlifting platform', 'parking', 'personal trainer', 'physical therapy', 'pool', 'power rack', 'quickdraws', 'resistance bands', 'rings', 'rock climbing shoes', 'rowers', 'sauna', 'shower', 'squat rack', 'stationary bikes', 'stretch area', 'towels', 'tredmill', 'tv', 'wifi', 'yoga mats', 'zumba']
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

#TODO wrapper to redirect to edit_gym if logged in
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
        #return '<form method="POST"><button type="submit">hi</button></form>'
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
        print user_email
        print "password when logging in: " + password
        print "password when logging in hashed: " + password
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
            print c.fetchall()
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        c.execute("SELECT UserId FROM GymManagers WHERE Email=%s LIMIT 1", (user_email,))
        user_id = c.fetchone()[0]
        c.execute("SELECT GymId FROM Gyms WHERE UserId=%s", (user_id,))
        result = c.fetchone()
        if result != None:
            print "login session user_id:"
            print user_id
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
                print "signup session user_id:"
                print user_id
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
        print user_email
        print "password when logging in: " + password
        print "password when logging in hashed: " + password
        c.execute("SELECT Password FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result == None:
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        else:
            result = result[0]
        print result
        if not validate_password(result, password):
            c.execute("SELECT * FROM GymGoers")
            print c.fetchall()
            flash("Credentials incorrect")
            return redirect(url_for("login"))
        c.execute("SELECT UserId FROM GymGoers WHERE Email=%s LIMIT 1", (user_email,))
        result = c.fetchone()
        if result != None:
            user_id = result[0]
            session['goer_id'] = user_id
            print user_id
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
                print "signup session user_id:"
                print user_id
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
    #TODO multiple price settings
    if 'manager_id' in session:
        user = session['manager_id']
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            #c.execute("SELECT GymId FROM Gyms")
            #taken_gyms = []
            #results = c.fetchall()
            #for result in results:
            #    taken_gyms.append(result[0])
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
        elif gym_id != None and 'goer_id' in session:
            c.execute("SELECT * FROM Gyms WHERE GymId=%s LIMIT 1", (gym_id,))
            gym = c.fetchone()
        else:
            flash("You have to log in before accessing this page")
            return redirect(url_for('login'))
        equipment = ""
        equipmentList = globalEquipmentList
        equipmentList.sort()
        j = 0
        if gym==None:
            if manager_logged_in:
                return redirect(url_for("select_gym"))
            requirements = ""
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
            while j < len(equipmentList):
                e = equipmentList[j]
                words = e.split(" ")
                i = 0
                while i < len(words):
                    words[i] = words[i].capitalize()
                    i = i + 1
                capE = " ".join(words)
                undE = "_".join(words)
                equipment = equipment + str('''<div class="checkbox"><label><input onchange="endisable('%s')" type="checkbox" class="equipmentcheckbox" name=%s><input id='%s' name='%s' type="text" value=0 size="2" maxamount="2" disabled>%s</label></div>'''%(e, e, e, undE, capE))
                j = j + 1
        else:
            gym_id = gym[IDCOL]
            requirements = gym[REQCOL]
            misc = gym[MISCCOL]
            monday = gym[MONDAYCOL]
            tuesday = gym[TUESDAYCOL]
            wednesday = gym[WEDNESDAYCOL]
            thursday = gym[THURSDAYCOL]
            friday = gym[FRIDAYCOL]
            saturday = gym[SATURDAYCOL]
            sunday = gym[SUNDAYCOL]
            while j < len(equipmentList):
                e = equipmentList[j]
                words = e.split(" ")
                i = 0
                while i < len(words):
                    words[i] = words[i].capitalize()
                    i = i + 1
                capE = " ".join(words)
                undE = "_".join(words)
                disabled = ""
                checked = " checked"
                if gym[j+EQUIPMENTSTARTCOL] <= 0:
                    disabled = " disabled"
                    checked = ""
                    equipment = equipment + str('''<div class="checkbox"><label><input onchange="endisable('%s')" type="checkbox" class="equipmentcheckbox" name=%s %s><input id='%s' name='%s' type="text" value=%s size="2" maxamount="2" %s>%s</label></div>'''%(e, e, checked, e, undE, gym[j+EQUIPMENTSTARTCOL], disabled, capE))
                j = j + 1
            hours = dictionarifyHours(monday, tuesday, wednesday, thursday, friday, saturday, sunday)
            print "hours: "
            print hours
            gym_imgs = os.listdir(os.path.join(app.config["UPLOAD_FOLDER"], gym[IDCOL]))
            price_num = gym[PRICECOL].split(":")[0]
            price_unit = gym[PRICECOL].split(":")[1]
            send_gym = False
        print send_gym
        return render_template("edit_gym.html", managerLoggedIn=manager_logged_in, gymId=gym_id, requirements=requirements, misc=misc, equipment=equipment, hours=hours, gymImgs=gym_imgs, priceNum=price_num, priceUnit=price_unit, sendGym=send_gym)

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
    #return json.dumps(hours)
    return hours

def allowed_file(filename):
    return '.' in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadImages', methods=['POST'])
def uploadImages():
    #TODO ALLOW USERS TO INPUT INFO
    if 'manager_id' in session and 'pic1' in request.files and 'gymId' in request.form:
        print request.files['pic1']
        file = request.files['pic1']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print filename
            print app.config['UPLOAD_FOLDER']
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
        print img_dir
        if os.path.exists(img_dir):
            os.remove(img_dir)
            return "Image removal successful!"
    return "Image removal unsuccessful"

@app.route('/gym/<id>')
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
        if not gym:
            c.execute("SELECT * FROM UserGymUpdates WHERE GymId=%s", (id,))
            info_available = c.fetchall()
            print info_available
            if not info_available:
                return render_template("new_gym.html", id=id, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)
            else:
                formatted_info = "<h1>" + info_available[0][NAMECOL] + "</h1>"
                for gymsql in info_available:
                    gym_name = gymsql[NAMECOL]
                    gym_price = gymsql[PRICECOL]
                    gym_req = gymsql[REQCOL]
                    gym_hours = dictionarifyHours(gymsql[MONDAYCOL], gymsql[TUESDAYCOL], gymsql[WEDNESDAYCOL], gymsql[THURSDAYCOL], gymsql[FRIDAYCOL], gymsql[SATURDAYCOL], gymsql[SUNDAYCOL])
                    gym_equipment = []
                    last_updated = gymsql[LASTUPDATECOL]
                    #formatted_info = formatted_info + str(gymsql) + "<br>"
                    #TODO USE USER EMAIL
                    formatted_info = formatted_info + "<br>" + last_updated + "<br>Price: " + str(gym_price) + "<br>Hours: " + str(gym_hours) + "<br>Equipment: " + str(gym_equipment)
                return render_template("new_gym_with_info.html", id=id, formattedInfo=formatted_info, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in)
        print gym
        c.execute("SELECT * FROM UserGymUpdates WHERE GymId=%s", (id,))
        results = c.fetchall()
        user_updates = False
        if results:
            #TODO MATCH PRICE, REQUIREMENTS, AND MISC
            user_updates = '''
<script src="https://cdn.datatables.net/1.10.9/js/jquery.dataTables.min.js"></script>
<style>
th, td {
white-space: nowrap;
}
#userGymUpdates {
overflow: auto;
}
</style>
<div id="userGymUpdatesContainer" style="width:100%">
<table id="userGymUpdates" class="display nowrap table table-bordered" style="width:100%">
'''
            table_head = "<thead><tr>"
            table_body = "<tbody><tr>"
            confirm_changes_row = "<tr>"
            for result in results:
                #user_updates = user_updates + "<td>"
                print result
                print result[USERCOL]
                user_email = get_user_email(result[USERCOL])
                table_head = table_head + "<th>" + user_email + "</th>"
                c.execute("SELECT * FROM UserGymVotes WHERE GymId=%s AND UpdaterId=%s AND Vote=1", (result[IDCOL], result[USERCOL]))
                upvotes = len(c.fetchall())
                c.execute("SELECT * FROM UserGymVotes WHERE GymId=%s AND UpdaterId=%s AND Vote=-1",(result[IDCOL], result[USERCOL]))
                downvotes = len(c.fetchall())
                confirm_changes_row = confirm_changes_row + "<td>Upvotes: <div id='" + user_email + "upvotes'>" + str(upvotes) + "</div><br>Downvotes: <div id='" + user_email + "downvotes'>" + str(downvotes) + "</div><br><button type='button' onclick='voteUserChange(&#34;" + id + "&#34;, &#34;" + user_email + "&#34;, 1)' class='btn'>Confirm Changes</button><br><button type='button' onclick='voteUserChange(&#34;" + id + "&#34;, &#34;" + user_email + "&#34;, -1)' class='btn'>Downvote Changes</button></td>"
                table_body = table_body + "<td>"
                for x in range(MONDAYCOL, SUNDAYCOL):
                    print "user input, then gym:"
                    print result[x]
                    print gym[x]
                    if result[x] != gym[x]:
                        for day in hoursColDict:
                            if hoursColDict[day] == x:
                                table_body = table_body + day + ": " + result[x]
                                #user_updates = user_updates + day + ": " + result[x]
                for x in range(EQUIPMENTSTARTCOL, EQUIPMENTSTARTCOL + len(globalEquipmentList)):
                    if result[x] != gym[x]:
                        table_body = table_body + "<br>" + globalEquipmentList[x-EQUIPMENTSTARTCOL] + ": " + str(result[x])
                        #user_updates = user_updates + "<td>" +  globalEquipmentList[x-EQUIPMENTSTARTCOL] + ": " + str(result[x]) + "</td>"
                table_body = table_body + "</td>"
            table_head = table_head + "</tr></thead>"
            table_body = table_body + "</tr>" + confirm_changes_row + "</tr></tbody>"
            print table_body
            #user_updates = user_updates + "</td>"
            user_updates = user_updates + table_head + table_body + """
</table>
<script>
$('#userGymUpdates').DataTable({
"scrollX": true
})
</script>
<script>
$('#userGymUpdatesContainer').hide();
</script>
</div>"""
            #user_updates = results
            print "user updated"
        else:
            print "user no update"
        name = gym[NAMECOL]
        price = gym[PRICECOL].replace(":", " per ")
        requirements = gym[REQCOL]
        misc = gym[MISCCOL]
        #hours = gym[HOURSCOL]
        hours="<br>Monday: " + gym[MONDAYCOL] + \
        "<br>Tuesday: " + gym[TUESDAYCOL] + \
        "<br>Wednesday: " + gym[WEDNESDAYCOL] + \
        "<br>Thursday: " + gym[THURSDAYCOL] + \
        "<br>Friday: " + gym[FRIDAYCOL] + \
        "<br>Saturday: " + gym[SATURDAYCOL] + \
        "<br>Sunday: <br>" + gym[SUNDAYCOL]
        hours = hours.replace(": <br>", ": Closed<br>")
        c.execute("SHOW COLUMNS FROM Gyms")
        #print c.fetchall()
        equipmentNames = []
        for b in c.fetchall()[EQUIPMENTSTARTCOL:]:
            equipmentNames.append(b[0].replace("_", " "))
        gym_imgs = os.listdir(os.path.join(app.config["UPLOAD_FOLDER"], gym[IDCOL]))
    return render_template("gym_page.html", name=name, price=price, requirements=requirements, misc=misc, hours=hours, gym=gym, equipmentNames=equipmentNames, addressCol=ADDRESSCOL, equipmentStartCol=EQUIPMENTSTARTCOL, lastUpdateCol=LASTUPDATECOL, gymImgs=gym_imgs, gymId=gym[IDCOL], adminLoggedIn=admin_logged_in, managerLoggedIn=manager_logged_in, goerLoggedIn=goer_logged_in, userUpdates=user_updates)

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
    '''if 'manager_id' in session:
        session.pop('manager_id')
    if 'gym_id' in session:
        session.pop('gym_id')
    if 'goer_id' in session:
        session.pop('goer_id')
    if 'admin_id' in session:
        session.pop('admin_id')'''
    session.clear()
    flash("You have successfully logged out")
    return redirect(url_for('index'))

@app.route('/addgym', methods=['POST'])
def add_gym():
    if request.method=='POST' and ('manager_id' in session or 'admin_id' in session):
        print request.form
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
                if 'gymType' not in request.form or request.form['price'] == '' or request.form['to1'] == '' or request.form['from1'] == '':
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
            print request.form
            gymId = request.form['gymId']
            gymName = request.form['gymName']
            gymLat = request.form['gymLat']
            gymLng = request.form['gymLng']
            gymType = request.form['gymType']
            gymAddress = request.form['gymAddress']
            print 'hi'
            gymPrice = request.form['price'] + ":" + request.form['priceunit']
            print 'hi'
            del formDict['gymId']
            del formDict['gymName']
            del formDict['gymLat']
            del formDict['gymLng']
            del formDict['gymType']
            del formDict['gymAddress']
            del formDict['price']
            del formDict['priceunit']
            #parse through hours- same as /browsegyms
            hoursIndex = 1
            #fromList = []
            #toList = []
            #dayList = []
            fromVar = request.form['from1']
            toVar = request.form['to1']
            dayVar = request.form['day1']
            hoursDict = {}
            while fromVar and toVar and dayVar:
                del formDict['from'+str(hoursIndex)]
                del formDict['to'+str(hoursIndex)]
                del formDict['day'+str(hoursIndex)]
                if fromVar != "" and toVar != "":
                    hoursVar = fromVar + "-" + toVar
                    daysList = []
                    if dayVar == "Weekends":
                        daysList = ["Saturday", "Sunday"]
                    elif dayVar == "Weekdays":
                        daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                    else:
                        daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    for day in daysList:
                        if day in hoursDict:
                            hoursDict[day] = hoursDict[day] + ";" + hoursVar
                        else:
                            hoursDict[day] = hoursVar
                    hoursIndex = hoursIndex + 1
                    fromVar = request.form.get("from"+str(hoursIndex), None)
                    toVar = request.form.get("to"+str(hoursIndex), None)
                    dayVar = request.form.get("day"+str(hoursIndex), None)
            requirements = ''#request.form['requirements']
            misc = ''#request.form['misc']
            timeNow = datetime.datetime.now().ctime()
            c.execute("SELECT * FROM Gyms WHERE UserId=%s AND GymId=%s LIMIT 1", (user_id, gymId))
            if c.fetchone()==None:
                '''insertGym = "INSERT INTO Gyms VALUES('%s', '%s'" % (gymId, gymName)
                insertGym = insertGym + ("%s", (user_id,))
                insertGym = insertGym + ", %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (gymLat, gymLng, gymAddress, gymType, gymPrice, hoursDict.get("Monday", ""), hoursDict.get("Tuesday", ""), hoursDict.get("Wednesday", ""), hoursDict.get("Thursday", ""), hoursDict.get("Friday", ""), hoursDict.get("Saturday", ""), hoursDict.get("Sunday", ""), requirements, misc, timeNow)'''
                ####TODO FIX HEXING OF USER_ID WHEN INSERTING, BC IT'S INSERTING AS 0X;FOIWJ;FW INSTEAD OF /X/SFWJF/W done?
                insertGym = "INSERT INTO Gyms VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                for equipment in globalEquipmentList:
                    insertGym = insertGym + ", 0"
                for gymClass in globalClassesList:
                    insertGym = insertGym + ", ''"
                insertGym = insertGym + ")"
                print insertGym
                print len(insertGym.split(","))
                c.execute("SELECT * FROM Gyms LIMIT 1")
                result = c.fetchone()
                print user_id
                c.execute(insertGym, (gymId, gymName, user_id, gymLat, gymLng, gymAddress, gymType, gymPrice, hoursDict.get("Monday", ""), hoursDict.get("Tuesday", ""), hoursDict.get("Wednesday", ""), hoursDict.get("Thursday", ""), hoursDict.get("Friday", ""), hoursDict.get("Saturday", ""), hoursDict.get("Sunday", ""), requirements, misc, timeNow))
                #con.commit()
                c.execute("SELECT * FROM Gyms WHERE UserId=%s", (user_id,))
                print "success?"
                for x in c.fetchall():
                    print x
                os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], gymId))
                flash("Gym added!")
                return redirect(url_for(next_redirect))
            return "Gym Already in your Gyms"
        return "Database Error"
    return "Malformed request"

@app.route('/api/getgyminfo', methods=['POST'])
def get_gym_info():
    if 'gymId' in request.form:
        gym_id = request.form['gymId']
        con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
        with con:
            c = con.cursor()
            c.execute("SELECT * FROM Gyms WHERE GymId=%s LIMIT 1", (gym_id,))
            print 'executed'
            result = c.fetchone()
            print result
            print gym_id
            c.execute("SELECT GymId FROM Gyms")
            results = c.fetchall()
            print "add gyms:"
            if result != None:
                print result
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
            print 'manager'
            user_id = session['manager_id']
            gym_id = session['gym_id']
            manager_logged_in = True
        elif 'goer_id' in session:
            user_id = session['goer_id']
            goer_logged_in = True
        infotype = request.form['type']
        gym_id = request.form['gymId']
        print infotype
        if infotype != "Equipment" and infotype != "Hours" and infotype != "Requirements" and infotype != "Misc":
            return "bruh stop screwing with the system"
        if infotype == "Equipment":
            equipment = json.loads(request.form['text'])
            if manager_logged_in:
                for lift in equipment:
                    print 'lift: ' + lift
                    c.execute("UPDATE Gyms SET " + lift + "=%s WHERE GymId=%s", (equipment[lift], gym_id))
            elif goer_logged_in:
                c.execute("SELECT * FROM UserGymUpdates WHERE UserId=%s AND GymId=%s LIMIT 1", (user_id, gym_id))
                if c.fetchone() == None:
                    print "user didnt update yet"
                    c.execute("SELECT * FROM Gyms WHERE GymId=%s", (gym_id,))
                    result = c.fetchall()
                    if not result:
                        print 'not result'
                        print request.form
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
        if infotype == "Hours":
            hours = json.loads(request.form['text'])
            hoursIndex = 1
            fromVar = hours['from1']
            toVar = hours['to1']
            dayVar = hours['day1']
            hoursDict = {}
            MondayHours = []
            TuesdayHours = []
            WednesdayHours = []
            ThursdayHours = []
            FridayHours = []
            SaturdayHours = []
            SundayHours = []
            while fromVar and toVar and dayVar and dayVar != "":
                print "from: " + fromVar
                print "to: " + toVar
                print "on: " + dayVar
                hoursVar = fromVar + "-" + toVar
                if dayVar == "Weekends" or dayVar == "Weekdays" or dayVar == "Everyday":
                    daysList = []
                    if dayVar == "Weekends":
                        daysList = ["Saturday", "Sunday"]
                    elif dayVar == "Weekdays":
                        daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                    else:
                        daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    for day in daysList:
                        print "day: " + day
                        if day in hoursDict:
                            hoursDict[day] = hoursDict[day] + ";" + hoursVar
                        else:
                            hoursDict[day] = hoursVar
                else:
                    if dayVar in hoursDict:
                        hoursDict[dayVar] = hoursDict[dayVar] + ";" + hoursVar
                    else:
                        hoursDict[dayVar] = hoursVar
                hoursIndex = hoursIndex + 1
                fromVar = hours.get("from"+str(hoursIndex), None)
                toVar = hours.get("to"+str(hoursIndex), None)
                dayVar = hours.get("day"+str(hoursIndex), None)
                print fromVar
                print toVar
                print dayVar
                '''if dayVar == "Weekdays":
                    c.execute("UPDATE Gyms SET Monday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Tuesday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Wednesday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Thursday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Friday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Weekends":
                    c.execute("UPDATE Gyms SET Saturday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Sunday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Everyday":
                    c.execute("UPDATE Gyms SET Monday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Tuesday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Wednesday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Thursday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Friday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Saturday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                    c.execute("UPDATE Gyms SET Sunday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Monday":
                    c.execute("UPDATE Gyms SET Monday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Tuesday":
                    c.execute("UPDATE Gyms SET Tuesday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Wednesday":
                    c.execute("UPDATE Gyms SET Wednesday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Thursday":
                    c.execute("UPDATE Gyms SET Thursday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Friday":
                    c.execute("UPDATE Gyms SET Friday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Saturday":
                    c.execute("UPDATE Gyms SET Saturday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))
                elif dayVar == "Sunday":
                    c.execute("UPDATE Gyms SET Sunday=%s WHERE UserId=%s AND GymId=%s", (hoursVar, user_id, gym_id))'''
                '''for timeIndex in range(len(fromList)):
                startTime = fromList[timeIndex]
                endTime = toList[timeIndex]
                day = dayList[timeIndex]
                print "s: " + startTime
                print "t: " + endTime
                print "day: " + day'''
            daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            print hoursDict
            for day in daysList:
                if day not in hoursDict:
                    #TODO FINISH THIS
                    hoursDict[day]=""
                    #return "Please enter values for every day of the week"
            for day in hoursDict:
                print day
                print hoursDict[day]
                c.execute("UPDATE GYMS SET " + day + "=%s WHERE UserId=%s AND GymId=%s", (hoursDict[day], user_id, gym_id))
            c.execute("SELECT * FROM Gyms")
            print c.fetchall()
            con.commit()
            update_time(gym_id)
            return "Update Successful!"
        info = request.form['text']
        c.execute("UPDATE Gyms SET " + infotype + "=%s WHERE User=%s AND GymId=%s", (info.replace('\\"', '&#34;'), user, gym_id))
        con.commit()
        update_time(gym_id)
        return "Update successful!"

def update_time(gym_id):
    con = MySQLdb.connect('127.0.0.1', 'admin', 'a098', 'pingyms')
    with con:
        c = con.cursor()
        #Change LastUpdate
        newUpdateTime = datetime.datetime.now().ctime()
        print gym_id
        print newUpdateTime
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
            print updater_id
            print voter_id
            c.execute("SELECT Vote FROM UserGymVotes WHERE GymId=%s AND UpdaterId=%s AND VoterId=%s LIMIT 1", (gym_id, updater_id, voter_id))
            result = c.fetchone()
            if result != None:
                if int(result[0]) == int(request.form['vote']) and int(result[0]) == 1:
                    return "You already voted in favor of this change"
                if int(result[0]) == int(request.form['vote']) and int(result[0]) == -1:
                    return "You already voted against this change"
                #c.execute("UPDATE UserGymVotes SET Vote=%d WHERE GymId='%s' AND UpdaterId='%s' AND VoterId='%s'" % (int(request.form['vote']), gym_id, updater_id, voter_id))
                if int(request.form['vote']) == 1:
                    c.execute("UPDATE UserGymVotes SET Vote=1 WHERE GymId=%s AND UpdaterId=%s AND VoterId=%s", (gym_id, updater_id, voter_id))
                elif int(request.form['vote']) == -1:
                    c.execute("UPDATE UserGymVotes SET Vote=-1 WHERE GymId=%s AND UpdaterId=%s AND VoterId=%s", (gym_id, updater_id, voter_id))
                else:
                    return "Error"
                return "Your vote has been changed!"
            if request.form['vote'] == "1":
                #c.execute("UPDATE UserGymVotes SET NumPlusVotes=NumPlusVotes+1 WHERE GymId=%s AND UserId=%s", (request.form['gym_id'], updater_id))
                c.execute("INSERT INTO UserGymVotes VALUES(%s, %s, %s, 1)", (gym_id, updater_id, voter_id))
                return "Thank you!"
            elif request.form['vote'] == "-1":
                #c.execute("UPDATE UserGymVotes SET NumMinusVotes=NumMinusVotes+1 WHERE GymId=%s AND UserId=%s", (request.form['gym_id'], updater_id))
                c.execute("INSERT INTO UserGymVotes VALUES(%s, %s, %s, -1)", (gym_id, updater_id, voter_id))
                return "Thank you!"
            #return request.form['vote']
            return "Error"
        #return "Error"
        #return request.form['gym_id'] + request.form['user_email']
        return "There was an error"

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
