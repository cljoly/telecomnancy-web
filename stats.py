#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import run, CalledProcessError
import subprocess
import os
import json
from json.decoder import JSONDecodeError

"""

PENSER À SYNCHRONISER CES CONSTANTES AVEC SETUP.SH

"""
# Clé SSH de Gitly
SSH_KEY = "./gitly_ssh.key"
# Dossier pour conserver les dépôts clonés le temps de faire des statistiques
CLONE_DIR = "./clone_dir"
# Chemin vers le script Gitinspector
GITINSPECTOR_PATH="gitinspector"


class InvalidKey(Exception):

    """Exception levée quand la clé SSH n’est pas valide"""

    def __init__(self):
        """TODO: to be defined1. """
        Exception.__init__(self)


class ErrorExtractingStat(Exception):

    """Exception levée quand gitinspector renvoie une erreur sur le dépot ou
    s’il écrit un JSON incorrect"""

    def __init__(self):
        """TODO: to be defined1. """
        Exception.__init__(self)


def get_stat_for(repo_url):
    """ Récupération d’un fichier JSON contenant les statistiques d’un dépôt
    donné

    :repo_url: Url du dépot
    :returns: TODO

    """
    repo_name = repo_url.split("/")[-1]

    env = os.environ.copy()
    env["GIT_SSH_COMMAND"] = "ssh -i ../{} -F /dev/null".format(SSH_KEY)
    try:
        # TODO Ajouter check=True pour que l’exception soit effectivement levée
        run(["git", "clone", repo_url, repo_name], env=env,
            capture_output=True, timeout=10, cwd=CLONE_DIR)
    except CalledProcessError:
        raise InvalidKey("Problème au clonage, la clé est sans doute invalide")
    wd = "{}/{}/{}".format(env["PWD"], CLONE_DIR, repo_name)
    gi = run([GITINSPECTOR_PATH, "--format=json", "-HlmrTw"], env=env,
             check=True, capture_output=True, cwd=wd)
    json_result = json.loads(gi.stdout)
    print(json_result)
    return json_result
