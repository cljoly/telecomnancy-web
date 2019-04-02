#!/usr/bin/env python3
from main import db

# Utilisateur élève
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gitlab_username = db.Column(db.String(80), unique=True, nullable=False)

# Enseignant
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gitlab_username = db.Column(db.String(80), unique=True, nullable=False)
    api_key = db.Column(db.String(16), unique=True, nullable=False)
