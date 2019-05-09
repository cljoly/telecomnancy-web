#!/usr/bin/env python3
# coding: utf-8

from flask import Flask, render_template, redirect, url_for, abort, \
    flash, request, send_from_directory
from flask_login import LoginManager, current_user, \
    logout_user, login_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, current_user, \
    logout_user, login_user
from typing import Dict
import gitlab
from pass_utils import hashnsalt


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
from gitlab_actions import gitlab_server_connection
from createNewActivity import create_new_activity, create_groups_for_an_activity_with_card_1


@app.route('/')
def homepage():
    """Homepage"""
    return render_template("homepage.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ signup """
    method = request.method
    if method == 'GET':
        return render_template("signup.html")
    elif method == 'POST':
        error = False
        form = request.form
        username = form.get('username')
        nb_user_with_username = User.query.filter(username == username).count()
        if nb_user_with_username > 0:
            flash("Un utilisateur portant ce nom existe déjà",
                  "danger")
            error = True
        firstname = form.get('firstname')
        name = form.get('name')
        email = form.get('email')
        nb_user_with_email = User.query.filter(email == email).count()
        if nb_user_with_email > 0:
            flash("Un utilisateur avec cette adresse mail existe déjà",
                  "danger")
            error = True
        password = form.get('password')
        password2 = form.get('password2')
        if password != password2:
            flash("Les mots de passe ne correspondent pas", "danger")
            error = True
        salt, h = hashnsalt(password)
        u = User(username=username, firstname=firstname, name=name,
                 email=email, password_hash=h, salt=salt,
                 gitlab_username='')
        db.session.add(u)

        gitlab_api_key = form.get('gitlab_api')
        if gitlab_api_key is not None:
            # L’utilisateur est prof
            t = Teacher(user=u, user_id=u.id, gitlab_key=gitlab_api_key)
            db.session.add(t)
        if not error:
            db.session.commit()
            flash("Vous êtes inscrit, identifiez-vous maintenant", 'success')
            return redirect(url_for("signin"))
        else:
            return redirect(url_for("signup"))


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
            if not gitlab_server_connection(current_user.username()):
                flash("Connexion à Gitlab impossible, veuillez générer une nouvelle clé d'API (access token) et la changer dans votre profil", 'danger')
                return redirect(url_for("my_profile"))
            else:
                flash('Connexion à Gitlab effectuée', 'success')
                return redirect(next_page or url_for('home'))

        return render_template("signin.html", next_page=next_page)
    return render_template("signin.html")


@app.route('/newactivity', methods=['GET', 'POST'])
@login_required
def new_activity():
    gl = gitlab_server_connection(current_user.username())
    if not gl:
        flash("Connexion à Gitlab impossible, veuillez générer une nouvelle clé d'API (access token) et la changer dans votre profil", 'danger')
        return redirect(url_for("my_profile"))

    if request.method == 'POST':

        result = request.form
        create_new_activity_result, activity_created = create_new_activity(result, db)

        if create_new_activity_result == 1:
            flash('Le module que vous souhaitez créer existe déjà. Activité non créée.', 'danger')
        elif create_new_activity_result == 2:
            flash('Veuillez indiquer un nom de module existant ou un nouveau module. Activité non créée.', 'danger')
        elif create_new_activity_result == 3:
            flash('Veuillez indiquer un nom d\'activité. Activité non créée.', 'danger')
        elif create_new_activity_result == 4:
            flash('Veuillez indiquer une date de début. Activité non créée.', 'danger')
        elif create_new_activity_result == 5:
            flash('Veuillez indiquer une date de fin. Activité non créée.', 'danger')
        elif create_new_activity_result == 6:
            flash('Veuillez indiquer au moins un enseignant référent. Activité non créée.', 'danger')
        elif create_new_activity_result == 7:
            flash('Veuillez indiquer un nombre d\'étudiant par groupe pour cette l\'activité. Activité non créée.', 'danger')
        elif create_new_activity_result == 8:
            flash('Veuillez sélectionner des étudiants pour cette l\'activité. Activité non créée.', 'danger')
        elif create_new_activity_result == 9:
            flash('Erreur lors de la création de l\'ajout de l\'activité dans la base de données. Activité non créée.', 'danger')
        elif create_new_activity_result == 0:
            flash('Activité ajoutée à la base de données', 'success')
            print(result)
            if int(result.get('numberOfStudents')) == 1:
                res = create_groups_for_an_activity_with_card_1(activity_created, db, gl)
                if res == 0:
                    flash('Création du dépôt de l\'activité effectuée', 'success')
                    flash('Tous les dépôts des élèves ont été créés', 'success')
                elif res == 1:
                    flash('Erreur de création du dépôt de l\'activité', 'danger')
                elif res == 2:
                    flash('Erreur dans le fork de l\'activité', 'danger')
            else:
                pass

        return render_template("newActivity.html")

    elif request.method == 'GET':
        # TODO: une fois le back fait, aller chercher les profs dans la BD
        teachers = Teacher.query.all()
        modules = Module.query.all()
        return render_template("newActivity.html", teachers=teachers, modules=modules)

    else:
        return redirect(url_for("homepage"))


@app.route('/newactivity/form/<int:activityId>')
def group_form(activityId):
    # TODO : aller chercher le nombre d'étudiants dans la BD
    numberOfStudents = 4
    return render_template("newGroupforAnActivityForm.html", activityId=activityId, numberOfStudents=numberOfStudents)


@app.route('/logout')
@login_required
def logout():
    """Redirect to homepage"""
    logout_user()
    return redirect(url_for("homepage"))


@app.route('/my_profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    """ My profile """

    if gitlab_server_connection(current_user.username()) is None:
        flash("Connexion à Gitlab impossible, veuillez générer une nouvelle clé d'API (access token) et la changer dans votre profil", 'danger')

    if request.method == 'GET':
        return render_template("my_profile.html", name=current_user.get_db_user().name,
                            firstName=current_user.get_db_user().firstname,
                            mail=current_user.get_db_user().email)

    elif request.method == 'POST':
        teacher = Teacher.query.filter_by(user_id=current_user.get_db_user().id).first()
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
                    flash('Les mots de passes doivent correspondre', "danger")
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
            return render_template("homepage.html")


@app.route('/forgottenPassword')
def forgotten_password():
    """ Forgotten password """
    return render_template("forgottenPassword.html")


@app.route('/activity/<int:activity_id>', defaults={'page': 1})
@app.route('/activity/<int:activity_id>/page/<int:page>')
def activity(page, activity_id):
    data_base_all_groups = Repository.query.filter_by(activity_id=activity_id).all()
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
@login_required
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
