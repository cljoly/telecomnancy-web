from database.db_objects import User, Teacher


def gitlab_server_connection(username):
    current_user = User.query.filter(User.username == username).first()
    print(current_user)
    print(current_user.id)
    current_teacher = Teacher.query.filter(Teacher.user_id == current_user.id).first()
    print(current_teacher)
    gitlab_key = current_teacher.gitlab_key
    print(gitlab_key)

