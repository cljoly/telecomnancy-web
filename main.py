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
from stats import *


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
from createNewActivity import create_new_activity, create_groups_for_an_activity_with_card_1, \
    create_groups_for_an_activity_with_multiple_card
import urllib.parse
from sqlalchemy.exc import IntegrityError as IntegrityError


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
    if request.method == 'POST':
        gl = gitlab_server_connection(current_user.username())
        if not gl:
            return redirect(url_for("my_profile"))

        result = request.form
        print(result)
        create_new_activity_result, activity_created, gitlab_activity_project = create_new_activity(result, db, gl)

        if create_new_activity_result == 1:
            flash('Le module que vous souhaitez créer existe déjà. Activité non créée.', 'danger')
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
        elif create_new_activity_result == 10:
            flash('Erreur de création du dépôt de l\'activité. Activité non créée', 'danger')
        elif create_new_activity_result == 11:
            flash('Une activité porte déjà le nom de l\'activité que vous souhaitez créer. Activité non créée', 'danger')
        elif create_new_activity_result == 0:
            flash('Activité ajoutée à la base de données', 'success')
            # print(result)
            # print(result.to_dict(flat=False).get('selectedStudents'))
            if int(result.get('numberOfStudents')) == 1:
                res = create_groups_for_an_activity_with_card_1(activity_created, db, gl, gitlab_activity_project, result.to_dict(flat=False).get('selectedStudents'))
                if res == 0:
                    flash('Création du dépôt de l\'activité effectuée', 'success')
                    flash('Tous les dépôts des élèves ont été créés', 'success')
                elif res == 1:
                    flash('Erreur dans l\'insertion dans la BD le fork de l\'activité', 'danger')
                elif res == 2:
                    flash('Erreur dans le fork de l\'activité', 'danger')
            elif 1 < int(result.get('numberOfStudents')) <= 6:
                url_form = create_groups_for_an_activity_with_multiple_card(activity_created, db)
                flash('Veuillez envoyer le formulaire créé à vos élèves pour que les groupes pour l\'activité puissent être créés', 'info')
                flash('Formulaire : ' + url_form, 'warning')

        teachers = Teacher.query.all()
        modules = Module.query.all()
        return render_template("newActivity.html", teachers=teachers, modules=modules)

    elif request.method == 'GET':
        gl = gitlab_server_connection(current_user.username())
        if not gl:
            return redirect(url_for("my_profile"))

        teachers = Teacher.query.all()
        modules = Module.query.all()
        return render_template("newActivity.html", teachers=teachers, modules=modules)

    else:
        return redirect(url_for("homepage"))


@app.route('/newactivity/form/<form_number>', methods=['GET', 'POST'])
def group_form(form_number):
    activity = Activity.query.filter(Activity.form_number == form_number).first()

    if not activity:
        flash("Le formulaire que vous demandez ne correspond à aucune activité", 'danger')
        return redirect(url_for("homepage"))

    if request.method == 'GET':
        return render_template("newGroupforAnActivityForm.html", form_number=form_number, numberOfStudents=activity.nbOfStudent, activityName=activity.name)

    elif request.method == 'POST':
        fields = request.form
        try:
            gl = gitlab.Gitlab('https://gitlab.telecomnancy.univ-lorraine.fr', private_token=activity.teacher.gitlab_key)
            gl.auth()
        except gitlab.exceptions.GitlabAuthenticationError as authentication_error:
            print("Erreur d'authentification sur gitlab :", authentication_error)
            flash("Veuillez demander à votre enseignant référent de mettre à jour sa clé d'API. Groupe non créé", 'danger')
            return render_template("newGroupforAnActivityForm.html", form_number=form_number, numberOfStudents=activity.nbOfStudent, activityName=activity.name)

        try:
            project = gl.projects.get(activity.id_gitlab_master_repo)

            # On vérifie que tous les utilisateurs existent sur giltab
            for i in range(1, activity.nbOfStudent):
                users = gl.users.list(username=fields.get("username%s" % i))
                if not users:
                    flash("Un des noms d'utilisateur Gitlab n'existe pas. Groupe non créé")
                    return render_template("newGroupforAnActivityForm.html", form_number=form_number, numberOfStudents=activity.nbOfStudent, activityName=activity.name)

            # Création du fork
            name = "%s %s" % (project.name, fields.get('repoName'))
            path = "%s_%s" % (project.path, urllib.parse.quote(fields.get('repoName')))
            fork = project.forks.create({"name": name, "path": path})

            # Récupération du projet (l'object Fork n'est pas un Project, donc il faut récupérer le bon object Project)
            fork_project = gl.projects.get(fork.id)

            for i in range(1, activity.nbOfStudent):
                user = gl.users.list(username=fields.get("username%s" % i))[0]
                fork_project.members.create({'user_id': user.id, 'access_level': gitlab.DEVELOPER_ACCESS})

            if fields.get("username%s" % activity.nbOfStudent):
                users = gl.users.list(username=fields.get("username%s" % activity.nbOfStudent))
                if not users:
                    flash("Un des noms d'utilisateur Gitlab n'existe pas. Groupe non créé")
                else:
                    user = users[0]
                    fork_project.members.create({'user_id': user.id, 'access_level': gitlab.DEVELOPER_ACCESS})

            # Liaison du repo à l'activité dans la BD
            repo = Repository(url=fork_project.web_url, activity=activity)

            try:
                db.session.add(repo)
                db.session.commit()
                flash('Dépôt créé avec succès', 'success')
                return render_template("newGroupforAnActivityForm.html", form_number=form_number, numberOfStudents=activity.nbOfStudent, activityName=activity.name)
            except IntegrityError as error:
                # Suppression du dépôt créé pour enlever tout résidu
                fork_project.delete()
                print(error)
                db.session.rollback()
                flash('Une erreur a été recontrée lors de la création du dépôt.', 'danger')
                return render_template("newGroupforAnActivityForm.html", form_number=form_number, numberOfStudents=activity.nbOfStudent, activityName=activity.name)
        except Exception as e:
            flash('Une erreur a été recontrée lors de la création du dépôt.', 'danger')
            print(e)
            return render_template("newGroupforAnActivityForm.html", form_number=form_number, numberOfStudents=activity.nbOfStudent, activityName=activity.name)


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

    if request.method == 'GET':
        if gitlab_server_connection(current_user.username()) is None:
            flash("Connexion à Gitlab impossible, veuillez générer une nouvelle clé d'API (access token) et la "
                  "changer dans votre profil", 'danger')
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
            if gitlab_server_connection(current_user.username()) is None:
                flash("Connexion à Gitlab impossible, veuillez générer une nouvelle clé d'API (access token) et la "
                      "changer dans votre profil", 'danger')
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


@app.route('/activity/<int:activity_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/activity/<int:activity_id>/page/<int:page>', methods=['GET', 'POST'])
def activity(page, activity_id):
    if request.method == 'GET':

        data_base_all_groups = Repository.query.filter_by(activity_id=activity_id).all()
        count = len(data_base_all_groups)
        all_groups = [Group(data_base_all_groups[i].url.split("/")[-1],
                            data_base_all_groups[i].url) for i in range(count)]
        activity_name = Activity.query.get(activity_id).name
        activity_link = Activity.query.get(activity_id).url_master_repo

        groups = get_groups_for_page(page, all_groups, count)

        if not groups and page != 1:
            abort(404)
        gl = gitlab_server_connection(current_user.username())
        if not gl:
            return redirect(url_for("my_profile"))
        activity_gitlab = gl.projects.get(gl.user.username + '/' + activity_name)
        branches = activity_gitlab.branches.list()
        list_branch_name = [b.name for b in branches]
        pagination = Pagination(page, PER_PAGE, count)
        return render_template("activity.html", pagination=pagination, groups=groups, activity_name=activity_name,
                               activity_link=activity_link, branches=list_branch_name)
    elif request.method == 'POST':
        data_base_all_groups = Repository.query.filter_by(activity_id=activity_id).all()
        count = len(data_base_all_groups)
        all_groups = [Group(data_base_all_groups[i].url.split("/")[-1],
                            data_base_all_groups[i].url) for i in range(count)]
        activity_name = Activity.query.get(activity_id).name
        activity_link = Activity.query.get(activity_id).url_master_repo

        groups = get_groups_for_page(page, all_groups, count)

        if not groups and page != 1:
            abort(404)
        gl = gitlab_server_connection(current_user.username())
        if not gl:
            return redirect(url_for("my_profile"))
        activity_gitlab = gl.projects.get(gl.user.username + '/' + activity_name)
        print(activity_gitlab)
        branches = activity_gitlab.branches.list()
        list_branch_name = [b.name for b in branches]
        for b in branches:
            if request.form.get(b.name):
                for projectTmp in activity_gitlab.forks.list():  # TODO : prendre la liste des projets cochets
                    mr_name = b.name
                    project = gl.projects.get(projectTmp.id)
                    branches_from_fork = [br.name for br in project.branches.list()]
                    while mr_name in branches_from_fork:
                        mr_name = mr_name + "X"
                    # print(mr_name)
                    project.branches.create({'branch': mr_name, 'ref': 'master'})
                    print("file tree : ")
                    print(activity_gitlab.repository_tree(ref=b.name))
                    for tmp_file in activity_gitlab.repository_tree(ref=b.name):
                        print(tmp_file)
                        file = activity_gitlab.files.get(file_path=tmp_file.get('path'), ref=b.name)
                        files_repo = project.repository_tree()
                        test_bool = False
                        for file_in_repo in files_repo:
                            if file_in_repo.get('path') == file.file_path:
                                test_bool = True
                        if not test_bool:
                            if file.ref == b.name:
                                project.files.create({
                                    'file_path': file.file_path,
                                    'branch': mr_name,
                                    'content': file.content,
                                    'author_email': current_user.get_db_user().email,
                                    'author_name': current_user.get_db_user().username,
                                    'encoding': file.encoding,
                                    'commit_message': 'Create ' + str(file.file_path)})
                        else:
                            test_file = project.files.get(file_path=tmp_file.get('path'), ref=mr_name)
                            test_file.content = file.content
                            test_file.save(branch=mr_name, commit_message='Update ' + str(file.file_path))
                    project.mergerequests.create({'source_branch': mr_name,
                                                  'target_branch': 'master',
                                                  'title': 'merge ' + b.name,
                                                  'labels': ['project', current_user.get_db_user().username]})
                flash("Merge request de " + b.name + " élaborée !", "success")
        pagination = Pagination(page, PER_PAGE, count)
        return render_template("activity.html", pagination=pagination, groups=groups, activity_name=activity_name,
                               activity_link=activity_link, branches=list_branch_name)


@app.route('/home/', defaults={'page': 1})
@app.route('/home/page/<int:page>')
@login_required
def home(page):
    """Home page"""
    count = Activity.query.filter(Activity.teacher_id == current_user.id).group_by(Activity.name).count()
    activities = get_activities_for_page(page)

    if not activities and page != 1:
        abort(404)
    pagination = Pagination(page, PER_PAGE, count)
    return render_template("home.html",
                           pagination=pagination,
                           activities=activities)


@app.route("/activity/<int:activity_id>/stats")
@login_required
def stats(activity_id):
    # TODO Attraper les exceptions pour afficher les messages d’erreur
    # adéquates à l’utilisateur
    # TODO Rendre générique pour n’importe quel projet
    # json_result = get_stat_for("git@gitlab.telecomnancy.univ-lorraine.fr:gitlab-bravo/ne-pas-supprimer-sert-aux-stats.git")
    import json
    json_result = json.loads('{"gitinspector":{"version":"0.5.0dev","repository":"pweb-2k19","report_date":"2019\/05\/14","changes":{"message":"The following historical commit information, by author, was found","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","commits":27,"insertions":615,"deletions":166,"percentage_of_changes":35.94},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","commits":32,"insertions":577,"deletions":224,"percentage_of_changes":36.86},{"name":"Lucas Fenouillet","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","commits":5,"insertions":107,"deletions":22,"percentage_of_changes":5.94},{"name":"lucas","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","commits":8,"insertions":71,"deletions":35,"percentage_of_changes":4.88},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","commits":16,"insertions":271,"deletions":85,"percentage_of_changes":16.38}]},"blame":{"message":"Below are the number of rows from each author that have survived and are still intact in the current revision","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","rows":412,"stability":67,"age":2.8,"percentage_in_comments":20.63},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","rows":410,"stability":71.1,"age":1.3,"percentage_in_comments":9.02},{"name":"lucas","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","rows":116,"stability":163.4,"age":3.8,"percentage_in_comments":7.76},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","rows":187,"stability":69,"age":1.2,"percentage_in_comments":4.28}]},"timeline":{"message":"The following history timeline has been gathered from the repository","period_length":"week","periods":[{"name":"2019W12","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"-+++++++++++++++++++++++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"++"},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"+"}],"modified_rows":88},{"name":"2019W13","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"--++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"--++"},{"name":"Lucas Fenouillet","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","work":"++++++++++++++++++++++++"},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"++++++++++++"}],"modified_rows":51},{"name":"2019W14","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"-------++++++++++++++++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"++"},{"name":"Lucas Fenouillet","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","work":"-++++++"}],"modified_rows":453},{"name":"2019W15","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"--------+++++++++++++++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"--------++++++++++++"},{"name":"Lucas Fenouillet","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","work":"."},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"+"}],"modified_rows":156},{"name":"2019W16","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"---++++++++++++++++++++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"----+++++"},{"name":"lucas","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","work":"---++"},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"---+++++"}],"modified_rows":286},{"name":"2019W17","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"--++++++++++++++++++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"------+++++++++++++++++"},{"name":"lucas","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","work":"-------++++++++++++++"},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"--++"}],"modified_rows":106},{"name":"2019W18","authors":[{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"----++++++++++++++++++++"},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"---+++++"}],"modified_rows":127},{"name":"2019W19","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"+++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"-------++++++++++++++++"},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","work":"---+++++++++++"}],"modified_rows":687},{"name":"2019W20","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","work":"+++++++++++++++"},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","work":"---+++++++++++++++++++++"},{"name":"lucas","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","work":"-+++++++"}],"modified_rows":219}]},"metrics":{"violations":[{"type":"cyclomatic-complexity","file_name":"main.py","value":185},{"type":"cyclomatic-complexity-density","file_name":"static\/script\/chart.min.js","value":4.5}]},"responsibilities":{"message":"The following responsibilities, by author, were found in the current revision of the repository (comments are excluded from the line count, if possible)","authors":[{"name":"JOLY Cl\u00e9ment","email":"clement.joly@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d4fcb2207796f013668ca53d6e930f42?default=identicon","files":[{"name":"main.py","rows":108},{"name":"database\/db_objects.py","rows":56},{"name":"stats.py","rows":50},{"name":"test_db.py","rows":43},{"name":"authentication.py","rows":39},{"name":"pass_utils.py","rows":18},{"name":"main_test.py","rows":11},{"name":"tools.py","rows":2}]},{"name":"Laury de Donato","email":"laury.de-donato@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/e4584087621b592f4946b4327c4eb970?default=identicon","files":[{"name":"main.py","rows":186},{"name":"createNewActivity.py","rows":115},{"name":"gitlab_test.py","rows":45},{"name":"gitlab_actions.py","rows":20},{"name":"database\/db_objects.py","rows":3},{"name":"authentication.py","rows":3},{"name":"tools.py","rows":1}]},{"name":"lucas","email":"lucas.fenouillet@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d558e83876f793641f29105cc55fce1b?default=identicon","files":[{"name":"tools.py","rows":65},{"name":"main.py","rows":39},{"name":"static\/script\/chart.min.js","rows":2},{"name":"test_db.py","rows":1}]},{"name":"morgan.ebandza@telecomnancy.eu","email":"morgan.ebandza@telecomnancy.eu","gravatar":"https:\/\/www.gravatar.com\/avatar\/d40db33892ae9e2c53427c8b5f2ed0a5?default=identicon","files":[{"name":"main.py","rows":146},{"name":"tools.py","rows":15},{"name":"test_db.py","rows":14},{"name":"authentication.py","rows":4}]}]},"extensions":{"message":"The extensions below were found in the repository history","used":["js","py"],"unused":["*","css","csv","html","md","sh","txt","yaml"]}}}')

    [histLabels, histValues, histLegend] = getHisto(json_result)

    changeLength = len(json_result['gitinspector']['changes']['authors'])
    changeLabels = [json_result['gitinspector']['changes']['authors'][i]['name']
                    for i in range(changeLength)]
    changeValues = [json_result['gitinspector']['changes']['authors'][i]['percentage_of_changes']
                    for i in range(changeLength)]

    [respNames, respValues, respFiles] = getResp(json_result)

    ignored = json_result['gitinspector']['extensions']['unused'][1::]

    return render_template('stats.html',
                           histValues=histValues,
                           histLabels=histLabels,
                           histLegend=histLegend,

                           doValues=changeValues,
                           doLabels=changeLabels,

                           respNames=respNames,
                           respValues=respValues,
                           respFiles=respFiles,

                           ignored=ignored)


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
