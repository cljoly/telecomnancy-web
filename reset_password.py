import smtplib
from sqlalchemy.exc import IntegrityError as IntegrityError
from database.db_objects import UrlPasswordHash
from datetime import datetime, timedelta
import uuid
from flask import url_for


def make_url(db, user):
    current_datetime = datetime.datetime.now()
    url_password_hash = UrlPasswordHash.query.filter(UrlPasswordHash.user == user, UrlPasswordHash.expire_date > current_datetime).first()
    if not url_password_hash:
        hash_for_url = uuid.uuid4().hex
        url_password_hash = UrlPasswordHash(hash=hash_for_url, user=user, expire_date=current_datetime+timedelta(days=1))
        try:
            db.session.add(url_password_hash)
            db.session.commit()
            return 0, url_password_hash.hash
        except IntegrityError as e:
            db.session.rollback()
            print(e)
            return 1, None
    else:
        return 0, url_for('reset_password', hash_url=url_password_hash.hash)


def send_email_to_reset_password(email_address, url):
    server = smtplib.SMTP_SSL(host="venus.telecomnancy.eu", port=465)
    server.connect(host='venus.telecomnancy.eu', port=465)
    server.login("gitlab-bravo@telecomnancy.eu", "prioriteaudirect")
    server.helo()

    sujet = "Réinitialisation de votre mot de passe"
    fromaddr = '"Gitly from TELECOM Nancy" <gitlab-bravo@telecomnancy.eu>'

    toaddrs = [email_address]

    message = """Bonjour,

    Voici le lien pour reinitialiser votre mot de passe : %s. 
    Il expirera dans 24 heures.

    Ceci est un mail automatique, merci de ne pas y repondre.

    Gitly for Gitlab TELECOM Nancy
    """ % url

    msg = """From: %s
    To: %s
    Subject: %s


    %s
             """ % (fromaddr, ",".join(toaddrs), sujet, message)
    server.sendmail(fromaddr, toaddrs, msg)

    try:
        server.sendmail(fromaddr, toaddrs, msg)
        return 0
    except smtplib.SMTPException as e:
        print(e)
        return 1
