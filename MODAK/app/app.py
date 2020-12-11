from flask import Flask
from MODAK import MODAK
from flask import jsonify, make_response
from flask import Flask, render_template, redirect, url_for, request
from flask import session

import json
app = Flask(__name__)

@app.route('/')
def index():
    file = "../app/modak.html"
    with open(file) as modak_html:
        return str(modak_html.read())

# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             session['logged_in'] = True
#             return redirect(url_for('home'))
#
#     return render_template('login.html', error=error)
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('home'))

@app.route("/optimise", methods=["POST"])
def modak_optimise():
    if request.is_json:
        # Parse the JSON into a Python dictionary
        req = request.get_json()
        # Print the dictionary
        print(req)
        m = MODAK('../conf/iac-model.ini')
        job_data = req
        link = m.optimise(job_data)

        job_data['job'].update({'job_script': link})
        res = make_response(jsonify(job_data), 200)
        return res

@app.route("/get_image", methods=["POST"])
def modak_get_image():
    if request.is_json:
        # Parse the JSON into a Python dictionary
        req = request.get_json()
        # Print the dictionary
        print(req)
        m = MODAK('../conf/iac-model.ini', upload=False)
        job_data = req
        container_runtime = m.get_opt_container_runtime(job_data)

        job_data['job'].update({'container_runtime': container_runtime})
        res = make_response(jsonify(job_data), 200)
        return res

@app.route("/get_job_content", methods=["POST"])
def modak_get_job_content():
    if request.is_json:
        # Parse the JSON into a Python dictionary
        req = request.get_json()
        # Print the dictionary
        print(req)
        m = MODAK('../conf/iac-model.ini', upload=False)
        job_data = req
        job_content = m.get_opt_job_script(job_data)

        job_data['job'].update({'job_content': job_content})
        res = make_response(jsonify(job_data), 200)
        return res

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')