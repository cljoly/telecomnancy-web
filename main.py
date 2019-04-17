#!/bin/env python3
# coding: utf-8


from flask import Flask, render_template, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from tools import *
from createNewGroup import *

app = Flask(__name__)
app.secret_key = ';??f6-*@*HmNjfk.>RLFnQX"<EMUxyNudGVf&[/>rR76q6T)K.k7XNZ2fgsTEV'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/main.sqlite'
db = SQLAlchemy(app)

@app.route('/')
def homepage():
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


@app.route('/newactivity', methods=['GET', 'POST'])
def new_activity():
    if request.method == 'POST':
        if create_new_group() == 1:
            flash('Le groupe a bien été créé', 'success')
        else:
            flash('Veuillez envoyer le formulaire créé à vos élèves pour que les groupes puissent être créés', 'info')
            flash('Formulaire : TODO','warning')
        return render_template("newActivity.html")

    elif request.method == 'GET':
        # TODO: une fois le back fait, aller chercher les profs dans la BD
        teachers = ("Captain", "Iron Man", "Thor", "Scarlett Witch", "Vision", "Black Widow", "Hulk")
        return render_template("newActivity.html", teachers=teachers)

    else:
        return redirect(url_for("homepage"))


@app.route('/newactivity/form/<int:activityId>')
def group_form(activityId):
    # TODO : aller chercher le nombre d'étudiants dans la BD
    numberOfStudents = 4
    return render_template("newGroupForm.html", activityId=activityId, numberOfStudents=numberOfStudents)


@app.route('/logout')
def logout():
    """Redirect to homepage"""
    # TODO : kill cookies / logout user
    return redirect(url_for("homepage"))


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


@app.route('/activity')
def activity():
    activityName = "Lightning XIII"
    return render_template("activity.html", activityName=activityName
                           , studentName1="Cloud Strife  ", nb_commits1="7  ", last_commit1="1997  "
                           , studentName2="Yuna  ", nb_commits2="10  ", last_commit2="2001  "
                           , studentName3="Terra Branford  ", nb_commits3="6  ", last_commit3="1994  "
                           , studentName4="Noctis Lucis Caelum  ", nb_commits4="15  ", last_commit4="2016  "
                           , studentName5="Tifa Lockhart", nb_commits5="7", last_commit5="1997"
                           , studentName6="Aeris Gainsborough", nb_commits6="7", last_commit6="1997"
                           , studentName7="Aeris Gainsborough", nb_commits7="7", last_commit7="1997"
                           , studentName8="Squall Leonhart", nb_commits8="8", last_commit8="1999"
                           , studentName9="Linoa Heartilly", nb_commits9="8", last_commit9="1999"
                           , studentName10="Lunafreya Nox Fleuret", nb_commits10="15", last_commit10="2016"
                           )


# todo: utiliser la bdd
allactivities = [Activity("My activity {}".format(i), 5 * i + 1) for i in range(100)]
#allactivities = []


@app.route('/home/', defaults={'page': 1})
@app.route('/home/page/<int:page>')
def home(page):
    """Home page"""
    count = len(allactivities)
    activities = get_activities_for_page(page, allactivities, count)

    if not activities and page != 1:
        abort(404)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template("home.html",
                           pagination=pagination,
                           activities=activities)


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
