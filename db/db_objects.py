#!/usr/bin/env python3
from main import db
from sqlalchemy.orm import relationship

# Utilisateur élève ou enseignants.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(120), unique=False, nullable=False)
    salt = db.Column(db.String(120), unique=True, nullable=False)

    gitlab_username = db.Column(db.String(80), unique=True, nullable=False)

# Propriétés propres à un utilisateur enseignant
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User')
    # API key
    gitlab_key = db.Column(db.String(80), unique=False, nullable=False)

# Matière : POO, CSD…
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Programmation orienté objet
    name = db.Column(db.String(120), unique=True, nullable=False)
    # POO
    short = db.Column(db.String(10), unique=True, nullable=False)
    # Enseignant responsable
    in_charge_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    in_charge = relationship("Teacher")

# Par exemple, TP1
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    year = db.Column(db.Integer)

# Groupe d’élèves ou de prof travaillant sur un dépôt, éventuellement d’une
# seule personne.
class UserSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Nom du groupe, par exemple G1, IL ou Memscarlo
    name = db.Column(db.String(120), unique=True, nullable=False)

# Chaque élève appartient à plusieurs groupes
class UserSetUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship("User")
    user_set_id = db.Column(db.Integer, db.ForeignKey('user_set.id'))
    user_set = relationship("UserSet")

# Dépot git particulier
class Repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=False, nullable=False)
    # Groupe d’élève en charge du dépot en charge du dépôt
    userset_id = db.Column(db.Integer, db.ForeignKey('user_set.id'))
    userset = relationship("UserSet")
