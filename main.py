#!/usr/bin/env python3
# coding: utf-8

from flask import Flask, render_template, redirect, url_for, abort, \
    flash, request, send_from_directory
from flask_login import LoginManager, current_user, \
    logout_user, login_user
from flask_sqlalchemy import SQLAlchemy

from createNewActivity import create_new_activity
import os
app = Flask(__name__)
app.secret_key = ';??f6-*@*HmNjfk.>RLFnQX"<EMUxyNudGVf&[/>rR76q6T)K.k7XNZ2fgsTEV'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/main.sqlite'
db = SQLAlchemy(app)

# XXX Nécessaire de le mettre ici pour avoir la bd
from authentication import login_form, AuthUser
from database.db_objects import User, Activity, Repository, Module, Teacher

db.create_all()

# Flask Login
login_manager = LoginManager()
login_manager.login_view = "signin"
login_manager.login_message = "S’il vous plaît, identifiez-vous."
login_manager.login_message_category = "warning"
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    """Récupération d’un utilisateur depuis la base de donnée, renvoie None
    s’il n’existe pas, renvoie un objet AuthUser sinon"""
    from database.db_objects import User
    db_user = User.query.get(int(user_id))
    auth_user = AuthUser(db_user)
    return auth_user

#Debug test

# Permet de tester les requêtes sur les activités
'''
from datetime import datetime

poo = Module(name="Programmation Orienté Objet", short_name="POO")
db.session.add(poo)
activity = Activity(id=1, module_id=poo.id, name="Lightning XIII", admingroup="Class 7",
                    start_date=datetime(year=2019, month=10, day=30),
                    year=2019, end_date=datetime(year=2019, month=10, day=31), nbOfStudent=15)
db.session.add(activity)
rep1 = Repository(url="https://fr.wikipedia.org/wiki/Final_Fantasy_VII", activity_id=activity.id)
db.session.add(rep1)
rep2 = Repository(url="https://fr.wikipedia.org/wiki/Final_Fantasy_VI", activity_id=activity.id)
db.session.add(rep2)
rep3 = Repository(url="https://fr.wikipedia.org/wiki/Final_Fantasy_X", activity_id=activity.id)
db.session.add(rep3)
'''
# Une activité


#db.session.commit()

from tools import *

@app.route('/')
def homepage():
    """Homepage"""
    return render_template("homepage.html", c="connected")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ signup """
    method = request.method
    if method == 'GET':
        return render_template("signup.html")
    elif method == 'POST':
        form = request.form
        username = form.get('username')
        firstname = form.get('firstname')
        name = form.get('name')
        email = form.get('email')
        password = form.get('password')
        # TODO Utiliser ces champs
        password2 = form.get('password2')
        gitlab_api = form.get('gitlab_api')
        # TODO Vérifier que les champs ne soient pas déjà définis et que les
        # mots de passe concordent
        # TODO Hacher les mots de passe
        u = User(username=username, firstname=firstname, name=name,
                 email=email, password_hash=password, salt='',
                 gitlab_username='')
        db.session.add(u)
        db.session.commit()
        flash("Vous êtes inscrit, identifiez-vous maintenant", 'success')
        return redirect(url_for("signin"))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """ Signin """
    method = request.method
    next_page = None
    if method == 'GET':
        # Redirection vers la page d’origine : si l’utilisateur arrive sur une
        # page p1 sans être identifié, il est redirigé vers la page signin et
        # il faut le rediriger vers p1 après identification. Par conséquent, on
        # doit conserver p1 dans l’argument next
        next_page = request.args.get('next')
        return render_template("signin.html", next_page=next_page)
    elif request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = form.get('password')
        next_page = request.form.get('next')
        if username is None:
            flash("Nom d’utilisateur requis", "danger")
        if password is None:
            flash("Mot de passe requis", "danger")

        auth_user = login_form(username, password)
        if auth_user is None:
            flash("Erreur d’identification : nom d’utilisateur ou mot de passe \
                  incorrect.", "danger")
        else:
            login_user(auth_user)
            flash("Vous êtes identifié", "success")
            return redirect(next_page or url_for('homepage'))

        return render_template("signin.html", next_page=next_page)
    return render_template("signin.html")


@app.route('/newactivity', methods=['GET', 'POST'])
# TOOD Décommenter ça une fois qu’on pourra s’identifier dans l’application
#@login_required
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
        modules = {
            "POO": "Programmation Orientée Objet",
            "C": "Langage C",
            "Prog web": "Programmation Web",
            "SD": "Structures de données"
        }
        modules = sorted(modules.items())
        return render_template("newActivity.html", teachers=teachers, modules=modules)

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
    logout_user()
    return redirect(url_for("homepage"))


@app.route('/my_profile', methods=['GET', 'POST'])
def my_profile():
    """ My profile """
    if request.method == 'GET':
        return render_template("my_profile.html", name=current_user.get_db_user().name,
                               firstName=current_user.get_db_user().firstname,
                               mail=current_user.get_db_user().email)
    elif request.method == 'POST':
        teacher = Teacher.query.filter_by(user_id=current_user.get_db_user().id)
        form = request.form
        api = form.get("newApi")
        pw = form.get("passwordAct")
        if api is not None:
            teacher.gitlab_key = api
            db.session.commit()
            flash("Changement de clé d'API effectué", "success")
            return render_template("my_profile.html", name=current_user.get_db_user().name,
                                   firstName=current_user.get_db_user().firstname,
                                   mail=current_user.get_db_user().email)
        elif pw is not None:
            npw = form.get("newPassword")
            npw2 = form.get("newPassword2")
            if pw == current_user.get_db_user().password_hash:
                if npw == npw2:
                    current_user.get_db_user().password_hash = npw
                    flash("Changement de mot de passe effectué", "success")
                    db.session.commit()
                    return render_template("my_profile.html", name=current_user.get_db_user().name,
                                           firstName=current_user.get_db_user().firstname,
                                           mail=current_user.get_db_user().email)
                else:
                    flash('Les mots de passes doivent matcher', "danger")
                    return render_template("my_profile.html", name=current_user.get_db_user().name,
                                           firstName=current_user.get_db_user().firstname,
                                           mail=current_user.get_db_user().email)
            else:
                flash("Erreur dans le mot de passe", "danger")
                return render_template("my_profile.html", name=current_user.get_db_user().name,
                                       firstName=current_user.get_db_user().firstname,
                                       mail=current_user.get_db_user().email)
        else:
            User.query.filter_by(id=current_user.get_db_user().id).delete()
            db.session.commit()
            logout_user()
            return render_template("homepage.html", c="disconnected")

@app.route('/forgottenPassword')
def forgotten_password():
    """ Forgotten password """
    return render_template("forgottenPassword.html")


@app.route('/activity/<int:activity_id>', defaults={'page': 1})  # TODO : voir pour les liens de la page avec les chnagements effectués.
@app.route('/activity/<int:activity_id>/page/<int:page>')
def activity(page, activity_id):
    activity_example_id = activity_id
    data_base_all_groups = Repository.query.filter_by(activity_id=activity_example_id).all()
    count = len(data_base_all_groups)
    all_groups = [Group(data_base_all_groups[i].url.split("/")[-1],
                        data_base_all_groups[i].url) for i in range(count)]
    #count = Repository.query.filter_by(Repository.activity_id == activity_example_id).count()
    #all_groups = [Group("Dalmatien {}".format(i), "/") for i in range(1, 102)]
    activity_name = Activity.query.get(activity_id).name

    groups = get_groups_for_page(page, all_groups, count)

    if not groups and page != 1:
        abort(404)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template("activity.html", pagination=pagination, groups=groups, activity_name=activity_name)

@app.route('/home/', defaults={'page': 1})
@app.route('/home/page/<int:page>')
def home(page):
    """Home page"""
    count = Activity.query.count()
    activities = get_activities_for_page(page,count)

    if not activities and page != 1:
        abort(404)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template("home.html",
                           pagination=pagination,
                           activities=activities)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='minutes/pictures/bd.jpg')


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
