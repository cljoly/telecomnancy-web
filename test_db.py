#!/usr/bin/env python3

from db.db_objects import User
from main import db
# Création des tables de la base de donnée
db.create_all()

# Quelques tests
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
    db.session.add(user)
    """
us1 = UserSet(name="17eme")
us2 = UserSet(name="18eme")
for us in [ us1, us2 ]:
    db.session.add(us)
usu1 = UserSetUser(user=u1, user_set=us1)
usu2 = UserSetUser(user=u2, user_set=us2)
usu3 = UserSetUser(user=u3, user_set=us2)
for usu in [ usu1, usu2, usu3 ]:
    db.session.add(usu)
    """
db.session.commit()
