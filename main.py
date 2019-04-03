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

from flask import Flask, render_template, abort
from tools import *


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


allgroups = [Group("My group {}".format(i), 5*i+1) for i in range(20)]
#allgroups = []


@app.route('/home/', defaults={'page': 1})
@app.route('/home/page/<int:page>')
def home(page):
    """Home page"""
    # todo: utiliser la bdd
    count = len(allgroups)
    groups = get_groups_for_page(page, allgroups, count)

    if not groups and page != 1:
        abort(404)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template("home.html",
                           pagination=pagination,
                           groups=groups)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5555, debug=True)
