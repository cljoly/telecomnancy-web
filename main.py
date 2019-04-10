# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, redirect, url_for

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def home():
    """Homepage"""
    return render_template("homepage.html", c="connected")


@app.route('/signup')
def signup():
    """ signup """
    return render_template("signup.html")


@app.route('/signin')
def signin():
    """ Signin """
    return render_template("signin.html")


@app.route('/newgroup1')
def newgroup1():
    teachers = ("Captain", "Iron Man", "Thor", "Scarlett Witch", "Vision", "Black Widow", "Hulk")
    return render_template("newgroup1.html", teachers=teachers)


@app.route('/logout')
def logout():
    """Redirect to homepage"""
    #TODO : kill cookies / logout user
    return redirect(url_for("home"))


@app.route('/myProfile')
def myProfile():
    """ My profile """
    return render_template("myProfile.html")


@app.route('/forgottenPassword')
def forgottenPassword():
    """ Forgottent password """
    return render_template("forgottenPassword.html")


@app.route('/profile')
def profile():
    return render_template("myProfile.html", name="Farron", firstName="Serah", mail="serah.farron@ffxiii.jp")


@app.route('/group')
def group():
    groupName = "Lightning XIII"
    return render_template("group.html", groupName=groupName
                           , studentName1="Cloud Strife  ", nb_commits1="7  ", last_commit1="1997  "
                           , studentName2="Yuna  ", nb_commits2="10  ", last_commit2="2001  "
                           , studentName3="Terra Branford  ", nb_commits3="6  ", last_commit3="1994  "
                           , studentName4="Noctis Lucis Caelum  ", nb_commits4="15  ",last_commit4="2016  "
                           , studentName5="Tifa Lockhart", nb_commits5="7", last_commit5="1997"
                           , studentName6="Aeris Gainsborough", nb_commits6="7", last_commit6="1997"
                           , studentName7="Aeris Gainsborough", nb_commits7="7", last_commit7="1997"
                           , studentName8="Squall Leonhart", nb_commits8="8", last_commit8="1999"
                           , studentName9="Linoa Heartilly", nb_commits9="8", last_commit9="1999"
                           , studentName10="Lunafreya Nox Fleuret", nb_commits10="15", last_commit10="2016"
                           )


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5555, debug=True)
