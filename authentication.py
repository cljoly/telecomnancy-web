#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import login_manager
from flask_login import UserMixin
import database.db_objects as db_objects


@login_manager.user_loader
def load_user(user_id):
    """Récupération d’un utilisateur depuis la base de donnée, renvoie None
    s’il n’existe pas, renvoie un objet AuthUser sinon"""
    db_user = db_objects.User.query.filter_by(id=int(user_id))
    auth_user = AuthUser(db_user)
    return auth_user


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
