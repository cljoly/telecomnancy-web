#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import run, CalledProcessError, TimeoutExpired
import os
import sys
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
GITINSPECTOR_PATH="../../gitinspector/gitinspector.py"

# Timeout pour cloner
CLONETIMEOUT=15
# Pour l’exécution des commandes en général
TIMEOUT=3


class InvalidKey(Exception):

    """Exception levée quand la clé SSH n’est pas valide"""

    def __init__(self, message):
        """TODO: to be defined1. """
        Exception.__init__(self)


class ErrorExtractingStat(Exception):

    """Exception levée quand gitinspector renvoie une erreur sur le dépot ou
    s’il écrit un JSON incorrect"""

    def __init__(self, message):
        """TODO: to be defined1. """
        Exception.__init__(self)


def get_stat_for(repo_url):
    """ Récupération d’un fichier JSON contenant les statistiques d’un dépôt
    donné

    :repo_url: Url du dépot
    :returns: TODO

    """
    # TODO SSH à partir d’http
    env = os.environ.copy()
    repo_name = repo_url.split("/")[-1]
    repo_abs_path = os.path.join(
        env["PWD"],
        CLONE_DIR, repo_name)

    # Suppression du dépôt si nécessaire
    if (os.path.isdir(repo_abs_path)):
        print("rm -rf ", repo_abs_path)
        run(["rm", "-rf", repo_abs_path])

    env["GIT_SSH_COMMAND"] = "ssh -i ../{} -F /dev/null".format(SSH_KEY)
    try:
        # TODO Ajouter check=True pour que l’exception CalledProcessError soit
        # effectivement levée
        gclone = run(["git", "clone", repo_url, repo_name], env=env,
                     timeout=CLONETIMEOUT, cwd=CLONE_DIR)
    except TimeoutExpired:
        raise InvalidKey("Problème au clonage, la clé est sans doute invalide \
                         (timeout)")
    if gclone.returncode != 0:
        raise InvalidKey("Problème au clonage, la clé est sans doute invalide")
    try:
        gi = run([GITINSPECTOR_PATH, "--format=json", "-HlmrTw"], env=env,
                 check=True, capture_output=True, cwd=repo_abs_path,
                 timeout=TIMEOUT)
    except:
        raise ErrorExtractingStat("gitinspector timed out")
    json_result = json.loads(gi.stdout)
    print(json_result)
    return json_result


def get_histo_plus(json_result):
    try:
        histLength = len(json_result['gitinspector']['timeline']['periods'])
        histLabels = []
        histValues = []
        histLegend = []
        for i in range(histLength):
            histLabels.append(json_result['gitinspector']['timeline']['periods'][i]['name'])
            for author in json_result['gitinspector']['timeline']['periods'][i]['authors']:
                if not (author['name'] in histLegend):
                    histLegend.append(author['name'])
                    histValues.append([])

        for i in range(histLength):
            authors = json_result['gitinspector']['timeline']['periods'][i]['authors']
            authorsNames = [author['name'] for author in authors]
            for j in range(len(histLegend)):
                author = histLegend[j]
                if author in authorsNames:
                    pos = authorsNames.index(author)
                    histValues[j].append(authors[pos]['work'].count('+'))
                else:
                    histValues[j].append(0)

        return [histLabels, histValues, histLegend]
    except KeyError:
        return [[],[],[]]


def get_histo_moins(json_result):
    try:
        histLength = len(json_result['gitinspector']['timeline']['periods'])
        histLabels = []
        histValues = []
        histLegend = []
        for i in range(histLength):
            histLabels.append(json_result['gitinspector']['timeline']['periods'][i]['name'])
            for author in json_result['gitinspector']['timeline']['periods'][i]['authors']:
                if not (author['name'] in histLegend):
                    histLegend.append(author['name'])
                    histValues.append([])

        for i in range(histLength):
            authors = json_result['gitinspector']['timeline']['periods'][i]['authors']
            authorsNames = [author['name'] for author in authors]
            for j in range(len(histLegend)):
                author = histLegend[j]
                if author in authorsNames:
                    pos = authorsNames.index(author)
                    histValues[j].append(authors[pos]['work'].count('-'))
                else:
                    histValues[j].append(0)

        return [histLabels, histValues, histLegend]
    except KeyError:
        return [[],[],[]]


def get_resp(json_result):
    try:
        respLength = len(json_result['gitinspector']['responsibilities']['authors'])
        respNames = []
        respValues = []
        respFiles = []
        for i in range(respLength):
            respNames.append(json_result['gitinspector']['responsibilities']['authors'][i]['name'])
            for file in json_result['gitinspector']['responsibilities']['authors'][i]['files']:
                if not (file['name'] in respFiles):
                    respFiles.append(file['name'])
                    respValues.append([])

        for i in range(respLength):
            files = json_result['gitinspector']['responsibilities']['authors'][i]['files']
            fileNames = [file['name'] for file in files]
            for j in range(len(respFiles)):
                file = respFiles[j]
                if file in fileNames:
                    pos = fileNames.index(file)
                    respValues[j].append(files[pos]['rows'])
                else:
                    respValues[j].append(0)

        return [respNames, respValues, respFiles]
    except KeyError:
        return [[],[],[]]
