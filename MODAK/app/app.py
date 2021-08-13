from flask import (  # redirect,; render_template,; session,; url_for,
    Flask,
    jsonify,
    request,
    send_from_directory,
)

from MODAK import MODAK

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(app.root_path, "index.html")


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
        m = MODAK()
        job_data = req
        link = m.optimise(job_data)

        job_data["job"].update({"job_script": link})

        return jsonify(job_data)


@app.route("/get_image", methods=["POST"])
def modak_get_image():
    if request.is_json:
        # Parse the JSON into a Python dictionary
        req = request.get_json()
        # Print the dictionary
        print(req)
        m = MODAK()
        job_data = req
        container_runtime = m.get_opt_container_runtime(job_data)

        job_data["job"].update({"container_runtime": container_runtime})

        return jsonify(job_data)


@app.route("/get_job_content", methods=["POST"])
def modak_get_job_content():
    if request.is_json:
        # Parse the JSON into a Python dictionary
        req = request.get_json()
        # Print the dictionary
        print(req)
        m = MODAK()
        job_data = req
        _, job_content = m.get_optimisation(job_data)

        job_data["job"].update({"job_content": job_content})

        return jsonify(job_data)


@app.route("/get_optimisation", methods=["POST"])
def modak_get_optimisation():
    if request.is_json:
        # Parse the JSON into a Python dictionary
        req = request.get_json()
        # Print the dictionary
        print(req)
        m = MODAK()
        job_data = req

        container_runtime, job_content = m.get_optimisation(job_data)
        job_data["job"].update(
            {"container_runtime": container_runtime, "job_content": job_content}
        )

        return jsonify(job_data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
