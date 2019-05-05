#!/usr/bin/env python3

import gitlab

# private token or personal token authentication
gl = gitlab.Gitlab('https://gitlab.telecomnancy.univ-lorraine.fr', private_token='fDeuQxkBbnz3TXyCnYn8')

# make an API request to create the gl.user object. This is mandatory if you
# use the username/password authentication.
gl.auth()


projects = gl.projects.list(visibility='private')
print(" User has access to %d private projects" % len(projects))

project = ''
source_namespace = 'Laury.De-Donato'
project_namespace = 'gitlab-bravo'
project_name = 'pcd_chocobar'

try:
    print("Récupération du projet %s/%s" % (project_namespace, project_name))
    project = gl.projects.get("%s/%s" % (project_namespace, project_name))
except Exception as e:
    print("Impossible de récupérer le projet %s/%s" % (project_namespace, project_name))
    print("Création du projet %s/%s" % (project_namespace, project_name))
    #project = gl.projects.create({'name': project_name})

try:
    print("Fork du projet %s/%s vers Gitlab Bravo" % (project_namespace, project_name))
    fork = project.forks.create({"name" : "Fork own chocobar", "path" : "fork_own_chocobar"})
except Exception as e:
    print("Impossible de forker %s/%s vers Gitlab Bravo" % (project_namespace, project_name))
    print(e)


forks = project.forks.list()
print("Project %s has %d forks" % (project_name, len(forks)))
for fork in forks:
    print(fork.name)