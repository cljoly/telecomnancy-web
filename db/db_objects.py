#!/usr/bin/env python3
from main import db

# Utilisateur élève
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(120), unique=True, nullable=False)
    salt = db.Column(db.String(120), unique=True, nullable=False)

    gitlab_username = db.Column(db.String(80), unique=True, nullable=False)

# Utilisateur enseignant
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(120), unique=True, nullable=False)
    salt = db.Column(db.String(120), unique=True, nullable=False)

    gitlab_username = db.Column(db.String(80), unique=True, nullable=False)
    # API key
    gitlab_key = db.Column(db.String(80), unique=True, nullable=False)

# Matière : POO, CSD…
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Programmation orienté objet
    name = db.Column(db.String(120), unique=True, nullable=False)
    # POO
    short = db.Column(db.String(10), unique=True, nullable=False)
    # Enseignant responsable
    in_charge_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

# Année scolaire, 2018 par exemple
class Year(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, unique=True)
