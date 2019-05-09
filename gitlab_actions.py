from database.db_objects import User, Teacher
import gitlab


def gitlab_server_connection(username):
    current_user = User.query.filter(User.username == username).first()
    current_teacher = Teacher.query.filter(Teacher.user_id == current_user.id).first()
    gitlab_key = current_teacher.gitlab_key
    print("clé API :", gitlab_key)
    try:
        gl = gitlab.Gitlab('https://gitlab.telecomnancy.univ-lorraine.fr', private_token=gitlab_key)
        gl.auth()
    except gitlab.exceptions.GitlabAuthenticationError as authentication_error:
        print("Erreur d'authentification sur gitlab :", authentication_error)
        return None

    return gl




