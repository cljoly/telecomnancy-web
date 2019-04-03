#!/usr/bin/env python3

from main import db
import sys
sys.path.insert(0, "./db")
from db_objects import User
# Création des tables de la base de donnée
db.create_all()

# Quelques tests
u1 = User(firstname="Victor", name="Hugo", email="victor@hugo.me", gitlab_username="hugo1802u")
u2 = User(firstname="Jules-Amédée", name="Barbey d’Aurevilly", email="jules_amedee_barbey_daurelvilly@telecomnancy.univ-lorraine.fr", gitlab_username="1808u")
u3 = User(firstname="Louis", name="de Rouvroy de Saint-Simon", email="louis-de-rouvroy-de-saint-simon@grand-duc-et-pair-de-france.fr", gitlab_username="derouvroydesaintsimon1675u")
user_list = [ u1, u2, u3 ]
for user in user_list:
    db.session.add(user)
db.session.commit()
