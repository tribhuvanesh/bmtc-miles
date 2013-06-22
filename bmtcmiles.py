import os
import datetime
import json
import tempfile
import subprocess
import re
import sys
from PIL import Image

from flask import Flask, request, redirect, send_from_directory, url_for, render_template
from werkzeug import secure_filename

CWD = os.getcwd()
UPLOAD_DIR = CWD + "/uploads/"

app = Flask(__name__)
app.debug = True

@app.route('/tickets/<username>/')
def panels(username):
    paneldir = UPLOAD_DIR + username + "/"
    panels = [name for name in os.listdir(paneldir) if not '.DS' in name]
    element = ''
    for panel in panels:
        element += '<td style="padding: 10px;">'
        element += '<img src="' + url_for('panel', username=username, filename=panel)  + '" height="320px"/>'
        element += '</td>'
    response = '''
    <!doctype html>
    <body bgcolor="black">
    <center>
    <table>
        <tr>'''
    response += element
    response += '''
                </tr>
            </table></center></body>'''
    return response

@app.route('/ticket/<username>/<filename>')
def panel(username, filename):
    return send_from_directory(UPLOAD_DIR + username + "/", filename)

@app.route('/upload/<username>/<filename>')
def upload(username, filename):
    paneldir = UPLOAD_DIR + username + "/"
    numpanels = str(len([name for name in os.listdir(paneldir)
                         if os.path.isfile(paneldir + name)]))
    response = dict(username=username, numpanels=numpanels)
    return json.dumps(response)

@app.route('/ocr/', methods=['POST'])
def ocr():
    if (not os.path.isdir(UPLOAD_DIR)):
        os.mkdir(UPLOAD_DIR)
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        timestamp = int(datetime.datetime.now().strftime("%s"))
        username = request.form['username']
        print "Got image from user:", username

        filepath = UPLOAD_DIR + username +  "/"
        fullfilename = filepath + filename
 
        print "Making dir:", filepath
        if (not os.path.isdir(filepath)):
            os.mkdir(filepath)
        print "Saving file:", os.path.join(filepath, filename)
        file.save(os.path.join(filepath, filename))

        print "OCR start"
        ocrScores = convert_img_to_price(os.path.join(filepath, filename))
        print "OCR end"
        validScores = sorted(filter( lambda x: x[0] < 200.0, ocrScores), key=lambda k: k[1], reverse=True)
        selectedScore = int(validScores[0][0]) if len(validScores) > 0 else 0

        # Resize image to reduce bandwidth on page load
        ticketImage = Image.open(os.path.join(filepath, filename))
        ticketWidth = ticketImage.size[0]
        ticketHeight = ticketImage.size[1]

        print "Size", ticketWidth, ticketHeight
        if (ticketWidth > 200):
            reductionFactor = 200.0 / ticketWidth * 2
            ticketWidth = int(ticketWidth * reductionFactor)
            ticketHeight = int(ticketHeight * reductionFactor)
            print "New size", ticketWidth, ticketHeight
            ticketImage = ticketImage.resize((ticketWidth, ticketHeight), Image.ANTIALIAS)
            ticketImage.save(os.path.join(filepath, filename))

        os.rename(os.path.join(filepath, filename), os.path.join(filepath, str(selectedScore) + '-' + str(timestamp) + '.jpg'))

    return redirect(url_for('leaders'))

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="/ocr/" method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=text name=username value=username>
        <input type=submit value=Upload>
    </form>
    '''
    """
    return render_template('index.html')

@app.route('/leaders/')
def leaders():
    try:
        users = [user for user in os.listdir(UPLOAD_DIR) if os.path.isdir(UPLOAD_DIR + user)]
    except OSError:
        return render_template('leaders.html')
    
    leaders = []
    for user in users:
        userData = {}
        userData['username'] = user
        tickets = [(re.split(r"[\.-]", ticket)[0], re.split(r"[\.-]", ticket)[1])
                    for ticket in os.listdir(UPLOAD_DIR + user)
                    if not '.DS' in ticket]
        userData['tickets'] = [(ticket[0], ticket[1]) for ticket in tickets]
        userData['totalmiles'] = sum([int(ticket[0]) for ticket in tickets])
        leaders.append(userData)

    leaders = sorted(leaders, key=lambda k: k['totalmiles'], reverse=True)

    return render_template('leaders.html', leaders=leaders)

def convert_price_to_score(price):
    '''
    Temporarily gives 1 point per Rs. 5, with a minumum of 1 point
    '''
    return price//5 if price >=5 else 1.0

def convert_img_to_price(path):
    '''
    Takes an img path as argument and returns a list of tuples (TicketPrice, Score)
    If path is invalid, throws an OSError
    '''
    # Use tesseract to write the OCR'd content to a tempfile
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tname = tfile.name
    tfile.close()
    try:
        subprocess.call(["tesseract", path, tname])

        # Extract the required information from the tempfile
        # Tesseract appends the filename with a .txt
        _tname = tname + '.txt'
        tfile = open(_tname)

        # Search for a floating point number
        matches = re.findall(r"\d+\.\d+", tfile.read())
        return map(lambda x : (x, convert_price_to_score(x)), map(float, matches))
    finally:
        # Discard the tempfile
        tfile.close()
        os.remove(tname)
        os.remove(_tname)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
