from flask import Flask
from MODAK import MODAK
from flask import jsonify, make_response
from flask import request
import json
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>MODAK</h1>'

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')