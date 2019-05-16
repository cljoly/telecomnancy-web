from database.db_objects import Activity, Module, Teacher, Repository
from sqlalchemy.exc import IntegrityError as IntegrityError
from datetime import datetime
import gitlab
import random
from flask import url_for
import smtplib


def create_new_activity(result, db, gl):

    # Vérification des modules : création d'un nouveau si demandé par l'utilisateur

    if result.get('moduleName') and result.get('moduleAbbreviation'):
        module = Module(name=result.get('moduleName'),
                        short_name=result.get('moduleAbbreviation')
                        )

        try:
            db.session.add(module)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return 1, None, None

    else:
        module = Module.query.filter(Module.short_name == result.get('module')).first()

    # Test des champs vides
    if result.get('activityName') is None:
        return 3, None, None

    if result.get('beginDate') is None:
        return 4, None, None

    if result.get('endDate') is None:
        return 5, None, None

    if result.get('selectedTeacher') is None:
        return 6, None, None

    if result.get('numberOfStudents') is None:
        return 7, None, None

    if result.get('selectedStudents') is None:
        return 8, None, None

    # Conversion des dates
    begin_date = datetime.strptime(result.get('beginDate'), '%Y-%m-%d')
    end_date = datetime.strptime(result.get('endDate'), '%Y-%m-%d')

    teacher = Teacher.query.filter(Teacher.id == result.get('selectedTeacher')).first()

    # Création du dépôt de l'activité
    # TODO insérer dates début et fin au repo
    potential_activity = Activity.query.filter(Activity.name == result.get('activityName')).first()
    if not potential_activity:
        try:
            project = gl.projects.create({'name': result.get('activityName'),
                                          'visibility': 'private',
                                          'issues_enabled': True,
                                          'merge_requests_enabled': True,
                                          'jobs_enabled': True,
                                          'wiki_enabled': True
                                          })
        except Exception as e:
            print("Erreur de création du dépôt de l'activité: ", e)
            return 10, None, None
    else:
        return 11, None, None

    # Création de la nouvelle activité
    new_activity = Activity(module_id=module.id,
                            name=result.get('activityName'),
                            year=int(datetime.now().year),
                            start_date=begin_date,
                            end_date=end_date,
                            nbOfStudent=result.get('numberOfStudents', type=int),
                            teacher_id=teacher.id,
                            id_gitlab_master_repo=project.id,
                            url_master_repo=project.web_url
                            )

    try:
        db.session.add(new_activity)
        db.session.commit()
    except IntegrityError as error:
        # Suppression du dépôt créé pour enlever tout résidu
        project.delete()
        print(error)
        db.session.rollback()
        return 9, None, None

    return 0, new_activity, project


def create_groups_for_an_activity_with_card_1(activity, db, gl, gitlab_activity_project, selected_students):

    # Fork du dépôt de l'activité pour créer un repo par élève
    try:
        # print("entrée fonc : ", selected_students)
        for username in selected_students:
            list_of_users_with_this_username = gl.users.list(username=username)
            # print(username)
            if list_of_users_with_this_username:
                user = list_of_users_with_this_username[0]
                name = "%s %s" % (gitlab_activity_project.name, user.name)
                path = "%s_%s" % (gitlab_activity_project.path, user.username)
                # print(user)

                # Création du fork
                fork = gitlab_activity_project.forks.create({"name": name, "path": path})

                # Récupération du projet (l'object Fork n'est pas un Project, donc il faut récupérer le bon object Project)
                fork_project = gl.projects.get(fork.id)

                # Ajout d'un membre en tant que développeur
                fork_project.members.create({'user_id': user.id, 'access_level': gitlab.DEVELOPER_ACCESS})

                # Liaison du repo à l'activité dans la BD
                repo = Repository(url=fork_project.web_url, ssh_url=fork_project.ssh_url_to_repo, activity=activity)

                try:
                    db.session.add(repo)
                    db.session.commit()
                except IntegrityError as error:
                    # Suppression du dépôt créé pour enlever tout résidu
                    fork_project.delete()
                    print(error)
                    db.session.rollback()
                    return 1

    except Exception as e:
        print("Erreur dans le fork :", e)
        return 2

    return 0


def create_groups_for_an_activity_with_multiple_card(activity, db):
    number = random.randint(1, 100000)
    activity.form_number = number
    db.session.commit()
    return url_for('group_form', form_number=number)


def send_email_to_students(url_form, activity, emails):
    server = smtplib.SMTP_SSL(host="venus.telecomnancy.eu",port=465)
    server.connect(host='venus.telecomnancy.eu',port=465)
    server.login("gitlab-bravo@telecomnancy.eu", "prioriteaudirect")
    server.helo()

    sujet = "Lien d'inscription pour l'activite %s" % activity.name.encode("ascii", "replace")
    fromaddr = '"Gitly from TELECOM Nancy" <gitlab-bravo@telecomnancy.eu>'

    toaddrs = emails

    message = """Bonjour,

Voici le lien pour vous inscrire a l'activite %s : %s.
        
Ceci est un mail automatique, merci de ne pas y repondre.
        
Gitly for Gitlab TELECOM Nancy
""" % (activity.name.encode("ascii", "replace"), url_form)

    msg = """From: %s
To: %s
Subject: %s
         
         
%s
         """ % (fromaddr, ",".join(toaddrs), sujet, message)
    server.sendmail(fromaddr, toaddrs, msg)

    try:
        server.sendmail(fromaddr, toaddrs, msg)
        return 0
    except smtplib.SMTPException as e:
        print(e)
        return 3
