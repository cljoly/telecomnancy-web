from database.db_objects import Activity, Module
from sqlalchemy.exc import IntegrityError as IntegrityError
from datetime import datetime


def create_new_activity(result, db):

    print(result)
    number_of_students = result.get('numberOfStudents', type=int)
    # number_of_students = int(request.form.get('numberOfStudents'))
    print("nb stud =", number_of_students)

    if result.get('module') is None:
        if result.get('moduleName') is not None and result.get('moduleAbbreviation') is not None:
            module = Module(name=result.get('moduleName'), short_name=result.get('moduleAbbreviation'))
            print("module nouveau :", module)

            try:
                db.session.add(module)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return 1

        else:
            return 2

    else:
        module = Module.query.filter(Module.short_name == result.get('module')).first()
        print("Module de la bd : ", module)

    print("module après if/else :", module)

    if result.get('activityName') is None:
        return 3

    if result.get('beginDate') is None:
        return 4

    if result.get('endDate') is None:
        return 5

    if result.get('selectedTeachers') is None:
        return 6

    if result.get('numberOfStudents') is None:
        return 7

    if result.get('selectedStudents') is None:
        return 8

    beginDate = datetime.strptime(result.get('beginDate'), '%Y-%m-%d')
    endDate = datetime.strptime(result.get('endDate'), '%Y-%m-%d')

    new_activity = Activity(module_id=module.id, name=result.get('activityName'), year=int(datetime.now().year), start_date=beginDate, end_date=endDate, nbOfStudent=result.get('numberOfStudents', type=int))

    try:
        db.session.add(new_activity)
        db.session.commit()
    except IntegrityError as error:
        print(error)
        db.session.rollback()
        return 9

    return 0
