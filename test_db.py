#!/usr/bin/env python3

from main import db
import sys
sys.path.insert(0, "./db")
from db_objects import User
# Création des tables de la base de donnée
db.create_all()

# Quelques tests
u1 = User(username="toto", email="toto@my.mail")
u2 = User(username="tata", email="tata@my.mail")
u3 = User(username="tutu", email="tutu@my.mail")
user_list = [ u1, u2, u3 ]
for user in user_list:
    db.session.add(user)
db.session.commit()
