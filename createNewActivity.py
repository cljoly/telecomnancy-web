from flask import request


def create_new_activity(result):

    print(result)

    number_of_students = int(request.form.get('numberOfStudents'))
    return number_of_students

