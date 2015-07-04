from flask import Flask, render_template, request
import urllib2
import json

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

@app.route('/api/getDetails', methods=['POST'])
def get_details():
    url = urllib2.urlopen(request.form['url'])
    d = json.loads(url.read())
    d = d['result']
    for k in d:
        print k
    data = {}
    if 'website' in d:
        data['website'] = "<a>" + d['website'] + "</a>"
    else:
        data['website'] = "Not available"
    if 'formatted_phone_number' in d:
        data['phone'] = d['formatted_phone_number']
    else:
        data['phone'] = "Not available"
    return json.dumps(data)

@app.route('/gymadminlogin')
def admin_login():
    return render_template("admin_login.html")

if __name__ == '__main__':
    app.debug = True
    app.run()
