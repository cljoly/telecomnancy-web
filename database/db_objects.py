#!/usr/bin/env python3
from main import db
# import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime


# Utilisateur élève ou enseignants
class User(db.Model):
    id = Column(Integer, primary_key=True)
    firstname = Column(db.String(80), unique=False, nullable=False)
    name = Column(db.String(80), unique=False, nullable=False)
    email = Column(db.String(120), unique=True, nullable=False)

    password_hash = Column(db.String(120), unique=False, nullable=False)
    salt = Column(db.String(120), unique=False, nullable=False)

    gitlab_username = Column(db.String(80), unique=True, nullable=False)


# Propriétés propres à un utilisateur enseignant
class Teacher(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'))
    user = relationship('User')
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


# Table d’association des enseignants à une activité
class ActivityTeacher(db.Model):
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, db.ForeignKey('teacher.id'))
    teacher = relationship('Teacher')
    activity_id = Column(Integer, db.ForeignKey('activity.id'))
    activity = relationship('Activity')


# Projet, TP…
class Activity(db.Model):
    id = Column(Integer, primary_key=True)
    # Matière
    module_id = Column(Integer, db.ForeignKey('module.id'))
    module = relationship("Module")
    # Par exemple, TP1
    name = Column(db.String(120), unique=False, nullable=False)
    # Par exemple IL ou groupe 1
    admingroup = Column(db.String(120), unique=False, nullable=False)
    year = Column(Integer)
    # Dates de début et fin
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    # Taille maximum d’un groupe
    nbOfStudent = Column(Integer, nullable=False)


# Table d’association élève / dépôt
class UserRepository(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'))
    user = relationship("User")
    user_set_id = Column(Integer, db.ForeignKey('repository.id'))
    user_set = relationship("Repository")


# Dépot git particulier
class Repository(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(db.String(120), unique=False, nullable=False)
    # Activity
    activity_id = Column(Integer, db.ForeignKey('activity.id'))
    activity = relationship("Activity")
