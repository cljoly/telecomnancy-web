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
from pass_utils import hashnsalt, verify_password
from stats import *


import os
app = Flask(__name__)
app.secret_key = ';??f6-*@*HmNjfk.>RLFnQX"<EMUxyNudGVf&[/>rR76q6T)K.k7XNZ2fgsTEV'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/main.sqlite'
db = SQLAlchemy(app)

# XXX Nécessaire de le mettre ici pour avoir la bd
from authentication import login_form, AuthUser
from database.db_objects import User, Activity, Repository, Module, Teacher, UrlPasswordHash
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
    if not db_user:
        return None
    auth_user = AuthUser(db_user)
    return auth_user


from tools import *
from gitlab_actions import gitlab_server_connection
from createNewActivity import create_new_activity, create_groups_for_an_activity_with_card_1, \
    create_groups_for_an_activity_with_multiple_card, send_email_to_students
import urllib.parse
from sqlalchemy.exc import IntegrityError as IntegrityError
from reset_password import send_email_to_reset_password, make_url
import datetime


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
            remember_me = form.get('check')
            if remember_me:
                login_user(auth_user, remember=True)
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
        usernames = list()
        emails = list()
        selected_students = result.to_dict(flat=False).get('selectedStudents')
        for student in selected_students:
            s = student.split(',')
            usernames.append(s[3])
            emails.append(s[2])

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

            if int(result.get('numberOfStudents')) == 1:
                res = create_groups_for_an_activity_with_card_1(activity_created, db, gl, gitlab_activity_project, usernames)
                if res == 0:
                    flash('Création du dépôt de l\'activité effectuée', 'success')
                    flash('Tous les dépôts des élèves ont été créés', 'success')
                elif res == 1:
                    flash('Erreur dans l\'insertion dans la BD le fork de l\'activité', 'danger')
                elif res == 2:
                    flash('Erreur dans le fork de l\'activité', 'danger')
            elif 1 < int(result.get('numberOfStudents')) <= 6:
                url_form = create_groups_for_an_activity_with_multiple_card(activity_created, db)
                url = "http://%s%s" % (request.host, url_form)
                res = send_email_to_students(url, activity_created, emails)
                if res == 0:
                    flash("Un mail vient d'être envoyé à vos étudiants pour s'inscrire et ainsi créer leur dépôt", 'success')
                elif res == 3:
                    flash("Erreur dans l'envoi du mail. Lien à envoyer aux élèves : " + url, 'warning')

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
            repo = Repository(url=fork_project.web_url, ssh_url=fork_project.ssh_url_to_repo, activity=activity)

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
        with open("gitly_ssh.key.pub", "r") as file:
            ssh_key = file.readline()
        return render_template("my_profile.html", name=current_user.get_db_user().name,
                               firstName=current_user.get_db_user().firstname,
                               mail=current_user.get_db_user().email, ssh_key=ssh_key)

    elif request.method == 'POST':
        with open("gitly_ssh.key.pub", "r") as file:
            ssh_key = file.readline()
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
                                   mail=current_user.get_db_user().email, ssh_key=ssh_key)
        elif pw is not None:
            npw = form.get("newPassword")
            npw2 = form.get("newPassword2")
            db_user = current_user.get_db_user()
            if verify_password(pw, db_user.salt, db_user.password_hash):
                if npw == npw2:
                    salt, pass_hash = hashnsalt(npw)
                    current_user.get_db_user().password_hash = pass_hash
                    current_user.get_db_user().salt = salt
                    flash("Changement de mot de passe effectué", "success")
                    db.session.commit()
                    return render_template("my_profile.html", name=current_user.get_db_user().name,
                                           firstName=current_user.get_db_user().firstname,
                                           mail=current_user.get_db_user().email, ssh_key=ssh_key)
                else:
                    flash('Les mots de passes doivent correspondre', "danger")
                    return render_template("my_profile.html", name=current_user.get_db_user().name,
                                           firstName=current_user.get_db_user().firstname,
                                           mail=current_user.get_db_user().email, ssh_key=ssh_key)
            else:
                flash("Erreur dans le mot de passe", "danger")
                return render_template("my_profile.html", name=current_user.get_db_user().name,
                                       firstName=current_user.get_db_user().firstname,
                                       mail=current_user.get_db_user().email, ssh_key=ssh_key)
        else:
            User.query.filter_by(id=current_user.get_db_user().id).delete()
            db.session.commit()
            logout_user()
            return render_template("homepage.html")


@app.route('/forgottenPassword', methods=['GET', 'POST'])
def forgotten_password():
    """ Forgotten password """
    if request.method == 'GET':
        return render_template("forgottenPassword.html")
    elif request.method == 'POST':
        email_address = request.form.get("email")
        print(email_address)
        if not email_address:
            flash("Veuillez entrez votre adresse email afin de pouvoir réinitialiser votre mot de passe", 'danger')
            return render_template("forgottenPassword.html")

        user = User.query.filter_by(email=email_address).first()
        if not user:
            flash("Aucun compte n'est associé à cette adresse mail. Réinitialisation de mot de passe impossible.", 'danger')
            return render_template("forgottenPassword.html")

        error, hashed = make_url(db, user)
        if error != 0:
            flash("Une erreur s'est produite, veuillez réessayer", 'danger')
            return render_template("forgottenPassword.html")
        after_root_url = url_for("reset_password", hash_url=hashed)
        url = "http://%s%s" % (request.host, after_root_url)
        res = send_email_to_reset_password(email_address, url)
        if res == 0:
            flash("Un mail vient de vous être envoyé pour réinitialiser votre mot de passe. Ce lien est valable 24 heures.", 'success')
            return render_template("forgottenPassword.html")
        if res == 1:
            flash("Erreur dans l'envoi du mail. Veuillez contacter l'administrateur du site", 'danger')
            return render_template("homepage.html")


@app.route('/reset_password/<hash_url>', methods=['GET', 'POST'])
def reset_password(hash_url):
    """ Reset password """
    if request.method == 'GET':
        current_datetime = datetime.datetime.now()
        url_password_hash = UrlPasswordHash.query.filter(UrlPasswordHash.hash == hash_url).first()
        if not url_password_hash:
            flash("Ce lien n'est pas valable.", "danger")
            return redirect(url_for('homepage'))
        viable_link = UrlPasswordHash.query.filter(UrlPasswordHash.hash == hash_url, UrlPasswordHash.expire_date > current_datetime).first()
        if not viable_link:
            flash('Lien de réinitialisation du mot de passe expiré.  Veuillez recommencer la procédure pour réinitialiser votre mot de passe.', 'danger')
            return redirect(url_for('homepage'))
        return render_template("reset_password.html")

    elif request.method == 'POST':
        current_datetime = datetime.datetime.now()
        url_password_hash = UrlPasswordHash.query.filter(UrlPasswordHash.hash == hash_url, UrlPasswordHash.expire_date > current_datetime).first()
        if not url_password_hash:
            flash('Lien de réinitialisation du mot de passe expiré. Veuillez recommencer la procédure pour réinitialiser votre mot de passe.', 'danger')
            return redirect(url_for('homepage'))
        new_password = request.form.get('password')
        new_password2 = request.form.get('password2')
        if not new_password or not new_password2:
            flash('Veuillez compléter les deux champs', 'danger')
            return render_template("reset_password.html")
        if new_password != new_password2:
            flash('Veuillez entrer deux mots de passes identiques', 'danger')
            return render_template("reset_password.html")
        salt, h = hashnsalt(new_password)
        url_password_hash.user.salt = salt
        url_password_hash.user.password_hash = h
        db.session.commit()
        flash('Votre mot de passe a été réinitialisé', 'success')
        return redirect(url_for('homepage'))


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
        activity_bdd = Activity.query.get(activity_id)

        groups = get_groups_for_page(page, all_groups, count)

        if not groups and page != 1:
            abort(404)
        gl = gitlab_server_connection(current_user.username())
        if not gl:
            return redirect(url_for("my_profile"))
        activity_gitlab = gl.projects.get(activity_bdd.id_gitlab_master_repo)
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
        activity_bdd = Activity.query.get(activity_id)

        groups = get_groups_for_page(page, all_groups, count)

        if not groups and page != 1:
            abort(404)
        gl = gitlab_server_connection(current_user.username())
        if not gl:
            return redirect(url_for("my_profile"))
        activity_gitlab = gl.projects.get(activity_bdd.id_gitlab_master_repo)
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
                    if mr_name == "master":
                        mr_name = mr_name + "X"
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
        if request.form.get("createIssue"):
            for projectTmp in activity_gitlab.forks.list():
                project = gl.projects.get(projectTmp.id)
                if request.form.get(project.path):
                    project.issues.create({'title': request.form.get("titleIssue"),
                                           'description': request.form.get("descIssue")})
            flash("Issue créée avec succès", "success")

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


@app.route("/stats/<int:repo_id>")
@login_required
def stats(repo_id):
    repo = Repository.query.get(repo_id)
    if not repo:
        flash("Id de dépôt invalide", "danger")
        return redirect(url_for('homepage'))
    try:
        json_result = get_stat_for(repo.ssh_url)
    except InvalidKey:
        print("Clé invalide")
        flash("Le clonage du dépôt a rencontré une erreur, veuillez ajouter \
              la clé SSH de votre profile dans Gitlab", "danger")
        return redirect(url_for("my_profile"), code=302)
    except ErrorExtractingStat:
        flash("GitInspector n’a pas pu être exécuté", "danger")
        return redirect(request.path, code=302)

    try:
        [histLabelsPlus, histValuesPlus, histLegendPlus] = get_histo_plus(json_result)
        [histLabelsMoins, histValuesMoins, histLegendMoins] = get_histo_moins(json_result)

        changeLength = len(json_result['gitinspector']['changes']['authors'])
        changeLabels = [json_result['gitinspector']['changes']['authors'][i]['name']
                        for i in range(changeLength)]
        changeValues = [json_result['gitinspector']['changes']['authors'][i]['percentage_of_changes']
                        for i in range(changeLength)]

        comLength = len(json_result['gitinspector']['blame']['authors'])
        comLabels = [json_result['gitinspector']['blame']['authors'][i]['name']
                        for i in range(comLength)]
        comValues = [json_result['gitinspector']['blame']['authors'][i]['percentage_in_comments']
                        for i in range(comLength)]

        [respNames, respValues, respFiles] = get_resp(json_result)

        ignored = json_result['gitinspector']['extensions']['unused'][1::]

        print(histValuesMoins)
        print(histLabelsMoins)
        print(histLegendMoins)

        return render_template('stats.html',
                               histValuesPlus=histValuesPlus,
                               histLabelsPlus=histLabelsPlus,
                               histLegendPlus=histLegendPlus,

                               histValuesMoins=histValuesMoins,
                               histLabelsMoins=histLabelsMoins,
                               histLegendMoins=histLegendMoins,

                               doValues=changeValues,
                               doLabels=changeLabels,

                               comValues=comValues,
                               comLabels=comLabels,

                               respNames=respNames,
                               respValues=respValues,
                               respFiles=respFiles,

                               ignored=ignored)

    except KeyError:
        flash("Erreur dans le chargement des statistiques", "danger")
        # TODO Lucas : il faudrait peut-être afficher ce message sur la page de
        # statistiques, non ? Je (Clément) mets ça en attendant
        return redirect(url_for('homepage'))


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
