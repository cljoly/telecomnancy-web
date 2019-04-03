#!/usr/bin/env python3

from main import db
import sys
sys.path.insert(0, "./db")
from db_objects import User, UserSet, UserSetUser
# Création des tables de la base de donnée
db.create_all()

# Quelques tests
u1 = User(firstname="Victor", name="Hugo", email="victor@hugo.me", password_hash="auie", salt="a", gitlab_username="hugo1802u")
u2 = User(firstname="Jules-Amédée", name="Barbey d’Aurevilly", email="jules_amedee_barbey_daurelvilly@telecomnancy.univ-lorraine.fr", password_hash="auie", salt="b", gitlab_username="1808u")
u3 = User(firstname="Louis", name="de Rouvroy de Saint-Simon", email="louis-de-rouvroy-de-saint-simon@grand-duc-et-pair-de-france.fr", password_hash="auie", salt="c", gitlab_username="derouvroydesaintsimon1675u")
user_list = [ u1, u2, u3 ]
for user in user_list:
    db.session.add(user)
us1 = UserSet(name="17eme")
us2 = UserSet(name="18eme")
for us in [ us1, us2 ]:
    db.session.add(us)
usu1 = UserSetUser(user=u1, user_set=us1)
usu2 = UserSetUser(user=u2, user_set=us2)
usu3 = UserSetUser(user=u3, user_set=us2)
for usu in [ usu1, usu2, usu3 ]:
    db.session.add(usu)
db.session.commit()
