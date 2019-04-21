#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_login import UserMixin
from database.db_objects import User


class AuthUser(UserMixin):

    """Représentation pour les utilisateur identifiés, construit par dessus
    les utilisateurs de la base de données"""

    # TODO Méthode pour savoir si l’utilisateur est un enseignant

    def __init__(self, db_user):
        """Crée l’objet à partir de la base de donnée

        :db_user: Objet User de la base de donnée

        """
        UserMixin.__init__(self)

        self._db_user = db_user
        self.id = db_user.id

    def display_name(self):
        return '{} {}'.format(self._db_user.firstname, self._db_user.name)

def login_form(username, password):
    """Fonction qui détermine si un couple (nom d’utilisateur, mot de passe)
    correspond à ce qui est enregistré dans la base de données, i.e. si
    l’utilisateur est bien inscrit. Si telle est le cas, elle renvoie un objet
    utilisateur identifié

    :username: Nom d’utilisateur, peut être None
    :password: Mot de pases, peut être None
    :returns: Un objet utilisateur identifié (AuthUser) ou None, si le couple
    nom d’utilisateur / mot de passe est incorrect.

    """
    if username is None or password is None:
        return None
    db_user = User.query.filter(User.email == username and
                                User.password_hash == password).first()
    if db_user is None:
        return None
    return AuthUser(db_user)
