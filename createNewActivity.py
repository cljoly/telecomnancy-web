from database.db_objects import Activity, Module
from sqlalchemy.exc import IntegrityError as IntegrityError
from datetime import datetime
import gitlab


def create_new_activity(result, db):

    if result.get('module') is None:
        if result.get('moduleName') is not None and result.get('moduleAbbreviation') is not None:
            module = Module(name=result.get('moduleName'), short_name=result.get('moduleAbbreviation'))
            print("module nouveau :", module)

            try:
                db.session.add(module)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return 1, None

        else:
            return 2, None

    else:
        module = Module.query.filter(Module.short_name == result.get('module')).first()
        print("Module de la bd : ", module)

    print("module après if/else :", module)

    if result.get('activityName') is None:
        return 3, None

    if result.get('beginDate') is None:
        return 4, None

    if result.get('endDate') is None:
        return 5, None

    if result.get('selectedTeachers') is None:
        return 6, None

    if result.get('numberOfStudents') is None:
        return 7, None

    if result.get('selectedStudents') is None:
        return 8, None

    beginDate = datetime.strptime(result.get('beginDate'), '%Y-%m-%d')
    endDate = datetime.strptime(result.get('endDate'), '%Y-%m-%d')

    new_activity = Activity(module_id=module.id, name=result.get('activityName'), year=int(datetime.now().year), start_date=beginDate, end_date=endDate, nbOfStudent=result.get('numberOfStudents', type=int))

    try:
        db.session.add(new_activity)
        db.session.commit()
    except IntegrityError as error:
        print(error)
        db.session.rollback()
        return 9, None

    return 0, new_activity


def create_groups_for_an_activity_with_card_1(activity, db, gl):

    # Création du dépôt de l'activité
    # TODO insérer dates début et fin au repo
    try:
        project = gl.projects.create({'name': activity.name, 'visibility': 'private', 'issues_enabled': True, 'merge_requests_enabled': True, 'jobs_enabled': True, 'wiki_enabled': True })
    except Exception as e:
        print("Erreur de création du dépôt de l'activité: ", e)
        return 1

    # Fork du dépôt de l'activité pour créer un repo par élève
    try:
        username_to_add = ("Laury.De-Donato", "toto")
        for username in username_to_add:
            list_of_users_with_this_username = gl.users.list(username=username)
            if list_of_users_with_this_username:
                user = list_of_users_with_this_username[0]
                name = "%s %s" % (project.name, user.name)
                path = "%s_%s" % (project.path, user.username)

                # Création du fork
                fork = project.forks.create({"name": name, "path": path})

                # Récupération du projet (l'object Fork n'est pas un Project, donc il faut récupérer le bon object Project)
                fork_project = gl.projects.get(fork.id)

                # Ajout d'un membre en tant que développeur
                fork_project.members.create({'user_id': user.id, 'access_level': gitlab.DEVELOPER_ACCESS})

    except Exception as e:
        print("Erreur dans le fork :", e)
        return 2


    return 0
