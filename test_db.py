#!/usr/bin/env python3
# Ne s'exécute plus
from database.db_objects import User, Teacher, Module, TeacherModule, Activity, Repository
from main import db
from sqlalchemy.exc import IntegrityError as IntegrityError
from datetime import datetime
# Création des tables de la base de donnée
db.create_all()

# Quelques utilisateurs
u1 = User(firstname="Victor", name="Hugo", email="victor@hugo.me",
          password_hash="auie", salt="a", gitlab_username="hugo1802u")
email2 = "jules_amedee_barbey_daurelvilly@telecomnancy.univ-lorraine.fr"
u2 = User(firstname="Jules-Amédée", name="Barbey d’Aurevilly",
          email=email2,
          password_hash="auie", salt="b", gitlab_username="1808u")
email3 = "louis-de-rouvroy-de-saint-simon@grand-duc-et-pair-de-france.fr"
u3 = User(firstname="Louis", name="de Rouvroy de Saint-Simon",
          email=email3,
          password_hash="auie", salt="c",
          gitlab_username="derouvroydesaintsimon1675u")
user_list = [u1, u2, u3]
for user in user_list:
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


# Ajout du même utilisateur
try:
    u1 = User(firstname="Victor", name="Hugo", email="victor@hugo.me",
            password_hash="auie", salt="a", gitlab_username="hugo1802u")
    db.session.add(u1)
    db.session.flush()
except IntegrityError:
    print("Erreur d’intégrité")

print("-8<-----")

# Saint-Simon est prof
t1 = Teacher(user=u1, gitlab_key="GITLAB-API-KEY")
db.session.add(t1)

# Un module
poo = Module(name="Programmation Orienté Objet", short_name="POO")
db.session.add(poo)
# Un responsable
r1 = TeacherModule(module=poo, teacher=t1)
db.session.add(r1)

# Une activité
activity = Activity(id=1, module_id=poo.id, name="Lightning XIII", admingroup="Class 7",
                    start_date=datetime(year=2019, month=10, day=30),
                    year=2019, end_date=datetime(year=2019, month=10, day=31), nbOfStudent=15)
db.session.add(activity)
rep1 = Repository(url="https://fr.wikipedia.org/wiki/Final_Fantasy_VII", activity_id=activity.id)
db.session.add(rep1)
rep2 = Repository(url="https://fr.wikipedia.org/wiki/Final_Fantasy_VI", activity_id=activity.id)
db.session.add(rep2)
rep3 = Repository(url="https://fr.wikipedia.org/wiki/Final_Fantasy_X", activity_id=activity.id)
db.session.add(rep3)


db.session.commit()

# Voir http://flask-sqlalchemy.pocoo.org/2.3/quickstart/ en complément
# Pour faire des requêtes SELECT, voir http://flask-sqlalchemy.pocoo.org/2.3/queries/
