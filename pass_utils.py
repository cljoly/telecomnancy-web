#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hmac
import uuid

def verify_password(password, salt, hashmac):
    """Vérification du mot de passe avec le sel

    :password: comme une chaine de char
    :salt: sel en hexa
    :salt: hashmac en hexa
    :returns: TODO

    """
    h = hmac.new(key=str.encode(salt), msg=str.encode(password))
    return hmac.compare_digest(h.hexdigest(), hashmac)

def hashnsalt(password):
    """ Mot de passe haché et salé  """
    salt = uuid.uuid4().hex
    h = hmac.new(key=str.encode(salt), msg=str.encode(password))
    return salt, h.hexdigest()
