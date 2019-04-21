#!/usr/bin/env python3
# coding: utf-8


from flask import Flask, render_template, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from tools import *
from createNewActivity import *
from database.db_objects import *

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
        if create_new_activity() == 1:
            flash('L\'activité a bien été créée', 'success')
        else:
            flash('Veuillez envoyer le formulaire créé à vos élèves pour que les groupes pour l\'activité puissent être créés', 'info')
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
    return render_template("newGroupforAnActivityForm.html", activityId=activityId, numberOfStudents=numberOfStudents)


@app.route('/logout')
def logout():
    """Redirect to homepage"""
    # TODO : kill cookies / logout user
    return redirect(url_for("homepage"))


@app.route('/myProfile')
def my_profile():
    """ My profile """
    return render_template("myProfile.html")


@app.route('/forgottenPassword')
def forgotten_password():
    """ Forgotten password """
    return render_template("forgottenPassword.html")


@app.route('/profile')
def profile():
    return render_template("myProfile.html", name="Farron", firstName="Serah", mail="serah.farron@ffxiii.jp")


@app.route('/activity/', defaults={'page': 1})  # TODO : voir pour les liens de la page avec les chnagements effectués.
@app.route('/activity/page/<int:page>')
def activity(page):
    """
    activity_example_id = 1
    all_groups = Repository.query.filter_by(Repository.activity_id == activity_example_id).all()
    count = Repository.query.filter_by(Repository.activity_id == activity_example_id).count()
    """
    all_groups = [Group("Dalmatien {}".format(i), "/") for i in range(1, 102)]  # TODO : requête à la base de données (remplacer)
    activity_name = "Cruella"  # TODO : requête à la base de données ou avec l'url (remplacer)
    count = len(all_groups)
    groups = get_groups_for_page(page, all_groups, count)

    if not groups and page != 1:
        abort(404)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template("activity.html", pagination=pagination, groups=groups, activity_name=activity_name)


# todo: utiliser la bdd
allactivities = [Activity("My activity {}".format(i), 5 * i + 1) for i in range(100)]


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
