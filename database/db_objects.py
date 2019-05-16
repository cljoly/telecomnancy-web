#!/usr/bin/env python3
from main import db
# import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime


# Utilisateur élève ou enseignants
class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(db.String(80), unique=True, nullable=False)
    firstname = Column(db.String(80), unique=False, nullable=False)
    name = Column(db.String(80), unique=False, nullable=False)
    email = Column(db.String(120), unique=True, nullable=False)

    password_hash = Column(db.String(120), unique=False, nullable=False)
    salt = Column(db.String(120), unique=False, nullable=False)

    gitlab_username = Column(db.String(80), unique=False, nullable=False)


# Propriétés propres à un utilisateur enseignant
class Teacher(db.Model):
    id = Column(Integer, primary_key=True)
    user = relationship('User')
    user_id = Column(Integer, db.ForeignKey('user.id'))
    # API key
    gitlab_key = Column(db.String(80), unique=False, nullable=False)


# Matière : POO, CSD…
class Module(db.Model):
    id = Column(Integer, primary_key=True)
    # Programmation orienté objet
    name = Column(db.String(120), unique=True, nullable=False)
    # POO
    short_name = Column(db.String(10), unique=True, nullable=False)


# Enseignant responsable, table d’association
class TeacherModule(db.Model):
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, db.ForeignKey('module.id'))
    module = relationship("Module")
    teacher_id = Column(Integer, db.ForeignKey('teacher.id'))
    teacher = relationship("Teacher")


# Projet, TP…
class Activity(db.Model):
    id = Column(Integer, primary_key=True)
    # Matière
    module_id = Column(Integer, db.ForeignKey('module.id'))
    module = relationship("Module")
    # Par exemple, TP1
    name = Column(db.String(120), unique=False, nullable=False)
    year = Column(Integer)
    # Dates de début et fin
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    # Taille maximum d’un groupe
    nbOfStudent = Column(Integer, nullable=False)
    # Lien vers le repo maitre
    id_gitlab_master_repo = Column(Integer, unique=False, nullable=False)
    url_master_repo = Column(db.String(300), unique=False, nullable=False)
    # Enseignant référent
    teacher_id = Column(Integer, db.ForeignKey('teacher.id'))
    teacher = relationship('Teacher')
    # Nombre aléatoire pour retrouver le formulaire associé si cardinalité > 1
    form_number = Column(Integer, nullable=True)


# Dépot git particulier
class Repository(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(db.String(120), unique=False, nullable=False)
    # Url de clone en SSH
    ssh_url = Column(db.String(120), unique=False, nullable=False)
    # Activity
    activity_id = Column(Integer, db.ForeignKey('activity.id'))
    activity = relationship("Activity")


# Hash des URL de réinitialisation de mot de passe et utilisateur associé
class UrlPasswordHash(db.Model):
    id = Column(Integer, primary_key=True)
    hash = Column(db.String(200), unique=False, nullable=False)
    # User associé
    id_user = Column(Integer, db.ForeignKey('user.id'))
    user = relationship("User")
    expire_date = Column(DateTime, nullable=False)
