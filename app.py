from flask import Flask, render_template, request
import urllib2
import json
#import psycopg2

app = Flask(__name__)

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
        return render_template("admin_loggedin.html", admin="admin")
    return render_template("admin_login.html")

@app.route('/editgyms')
def edit_gyms():
    return render_template("edit_gyms.html", gymName="Blink Fitness")

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
    return json.dumps(data)

@app.route('/api/addgym', methods=['POST'])
def add_gym():
    return "Gym added!"

if __name__ == '__main__':
    app.debug = True
    app.run()
