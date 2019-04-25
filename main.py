#!/usr/bin/env python3
# coding: utf-8

from createNewActivity import create_new_activity
from flask import Flask, render_template, redirect, url_for, abort, \
    flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, current_user, \
    logout_user, login_user

app = Flask(__name__)
app.secret_key = ';??f6-*@*HmNjfk.>RLFnQX"<EMUxyNudGVf&[/>rR76q6T)K.k7XNZ2fgsTEV'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/main.sqlite'
db = SQLAlchemy(app)

# XXX Nécessaire de le mettre ici pour avoir la bd
from authentication import login_form, AuthUser
from database.db_objects import User
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
    logout_user()
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
