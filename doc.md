# Sources

- https://www.sqlalchemy.org/, documentation de l’ORM
- http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
- https://getbootstrap.com/docs/4.3/getting-started/introduction/ Documentation bootstrap
- https://openclassrooms.com/fr/courses/2984401-apprenez-a-coder-avec-javascript
- https://devdocs.io/javascript/
- http://flask.pocoo.org/docs/1.0/quickstart/
- https://www.w3schools.com/
- https://docs.python.org/3/
- https://material.io/tools/icons/?search=G&icon=label_important&style=sharp

## Déploiement sur Google App Engine

Nous n'avons pas effectué le déploiement de l'application sur Google App Engine pour plusieurs raisons :
- nous avons commencé le projet sans penser au déploiement et nous n'avons donc pas utilisé les outils de Google
- les permissions sur un serveur de ce type ne sont pas représentatives de celles que l'on aurait si on était si le site était déployé depuis les serveurs de l'école

Aussi, pour que le déploiement sur Google App Engine soit possible et fonctionnel au même niveau que celui sur Heroku, il aurait fallu que nous utilisions le cloud de google pour la base de données et surtout pour cloner les dépôts des élèves dont on veut récupérer les statistiques. La limite de taille offerte par le cloud de Google étant assez faible, nous avons estimé qu'il serait compliquer d'envisager une utilisation sur le long terme de cette solution sachant que l'application devrait être déployé sur les serveurs de l'école.

## Pagination

La pagination sert pour les pages liées aux activités afin de limiter le nombre de dépôts ou de groupes à l'écran en même temps et de faciliter la navigation. La liste des entrées du tableau est calculée dynamiquement en ne faisant des requêtes que sur la partie concernée. Pour l'interface on crée un itérable qui indique quels numéros de page sont clickables en dessous du tableau. Enfin on se sert de l'url pour savoir à quelle page l'utilisateur se situe.

## Difficultés rencontrées:
la manipulation des itérables en Python ne m'était plus très familière, il m'a fallu faire quelques recherches dans la documentation.

# Gestion de comptes

Les accès utilisateurs sont gérés avec un système de comptes protégés par mots de passe. Ceux-ci sont hachés et salés, on n'en conserve que le hash dans la base de donnée. Un utilisateur non connecté voit ses options restreintes dans le menu d'accueil tandis qu'un utilisateur connecté peut naviguer dans ses pages grâce à ce même menu. Pour ce dernier la page d'accueil (/home) contient déjà des informations le concernant.

# Connexion avec Gitlab

TODO: Comment ça marche?
Le service vérifie en permanence la validité de la clef d'API fournie. Si la clef d'API de l'utilisateur n'est plus valide, celui-ci se trouve alors redirigé sur la page de profil pour en changer.

# Menu de navigation

Une barre de navigation est en permanence affichée en haut du site. À partir de celle-ci un utilisateur connecté peut se déplacer vers sa page d'accueil (liste de ses activités) ou son profil, et se déconnecter. Un utilisateur non connecté peut s'inscrire, revenir à la page d'accueil ou se connecter.

# Route : /homepage

La page **homepage** est la page d'accueil de Gitly, seul un message de bienvenue, le logo de Gitlab et la barre de navigation sont affichés sur cette page. Lorsque certains problèmes surviennent sur le site, il arrive que l'utilisateur soit redirigé sur cette page.

# Route : /home

Cette page regroupe les activités qui concernent un professeur connecté. Si un utilisateur non connecté essaye d'accéder cette page, il est redirigé sur l'accueil. On utilise la pagination pour naviguer dans les entrées du tableau. En backend sont faites des requêtes SQL pour la page concernée. Depuis cette page sont accessibles les les pages des activités grace aux liens situés à gauche de leurs entrées dans le tableau, et la page de création de groupe.

# Route : /my_profile

La page **my_profile** permet de présenter toutes les informations que l'application possède sur l'utilisateur. L'utilisateur peut également y modifier son mot de passe et y mettre à jour sa clé d'API Gitlab. On y trouve également la clé SSH que l'utilisateur doit ajouter à Gitlab pour pouvoir générer les statistiques des dépôts git des étudiants.

# Route : /activity/id

La page **activity** permet de présenter ce que l'on appelle une activité dans l'application. Une activité est un regroupement de dépôts gits géré par le professeur responsable de cette activité (par exemple un TP ou un projet). Une fois qu'une activité est créée, il n'est plus possible de la modifier (une amélioration possible serait de permettre la modification d'une activité). Sur la page d'une activité, on peut accéder effectuer plusieurs actions :
- Accéder au dépôt qui a été fork pour créer les dépôts des élèves (le répertoire parent)
- Accéder aux dépôts de chacun des élèves ou groupes d'élèves selon le type d'activité
- Accéder aux statistiques des dépôts des élèves
- Créer une Merge Request d'une branche du dépôt parent sur les dépôts des élèves
- Créer des Issues sur une sélection de dépôts parmis les dépôts des étudiants

L'une des principales difficultés rencontrée pour l'élaboration de cette page est la création de la Merge Request sur les dépôts des élèves. En effet, l'API de Gitlab ne permet pas de répercuter une Merge Request qui a été faite sur le dépôt parent sur les dépôts créé avec le fork. Il faut donc pour chaque dépôt copier l'intégralité de la branche dont on souhaite faire une Merge Request dans une nouvelle branche qui porte le même nom si celle-ci n'existe pas déjà et la renomme si c'est le cas (on peut également noter qu'à partir d'un certain nombre de branches, l'API de gitlab ne permet pas de récupérer l'intégralité des branches d'un d'un dépôt et il devient donc impossible de vérifier que la branche n'existe pas déjà).
