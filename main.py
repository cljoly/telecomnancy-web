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

from flask import Flask, render_template
import time


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.route('/register')
def register():
    """ register """
    return render_template("register.html")


@app.route('/signin')
def signin():
    """ Signin """
    return render_template("signin.html")


@app.route('/home')
def home():
    """Home page"""
    return render_template("home.html")

    #g = Group("My group", 1000)
    #return render_template("home.html", groups=[g])


class Group:
    name = ''
    c_date = ''
    d_date = ''
    count = 0

    def __init__(self, name, count):
        self.c_date = time.strftime("%d/%m/%Y")
        self.name = name
        self.count = count


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5555, debug=True)
