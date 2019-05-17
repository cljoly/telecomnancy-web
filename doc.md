# Gestion de projet

Nous avons utilisé la fonctionnalité d’issue de Gitlab pour nous coordonner et
nous répartir le travail. Nous avons organisé les issues par release (encart
milestone de Gitlab) et avons assigné une personne (ou plusieurs dans certains
cas). Nous avons initialement utilisé aussi la possibilité de fixer des dates
pour les issues. Ceci s’est avéré peu souple et inadapté à notre emploi du
temps : nous étions parfois ammenés à avancer ou repousser une réunion et les
dates étaient alors incohérentes.

En ce qui concerne les réunions, nous avons fait le point sur l’avancement à
une fréquence hebdomadaire. Nous avons aussi souvent profité de ces séances
pour travailler ensemble et nous mettre d’accord sur les parties communes de
l’application. Par exemple, nous avons dû décider du vocabulaire et de la
structure de la base de données en commun, puisque cela impactait tout le monde.


Nous avons enfin pris en charge chacun une ou plusieurs pages, selon leur
complexité : certains membres du groupe avaient des pages simples et ont donc
pris en charge plusieurs pages. Les release ont été faîtes sur les dernières
semaines du projet, parce qu’à cause de cette parallélisation des tâches, nous
n’avons eu des ensemble de fonctionnaliés cohérents qu’assez tardivement.

# Vocabulaire

Nous avons pris les conventions suivantes. On appelle :
- activité
- dépôt
- …

# Choix techniques

Nous avons choisi d’utiliser une base de donnée SQLite avec l’ORM SQLAlchemy.
SQLite présente l’avantage d’être extrement simple à installer et de ne pas
présenter de latence particulière, contrairement à une base de donnée de type
PostgreSQL. L’inconvénient de ce choix est qu’on ne pourrait pas avoir un grand
nombre d’utilisateur et déployer plusieurs serveur avec la même application
pour un seul serveur serveur de base de donnée, comme vu dans le MOOC.
Toutefois, cette inconvénient est minime, dans la mesure où peu d’utilisateurs
seront ammenés à utiliser le service (quelques enseignants de Télécom Nancy).
De plus, l’ORM est générique et permettrait de passer à un autre moteur de base
de donnée de manière transparente, sans adaptation particulière de notre code.

De plus, nous faisons appel à l’API de Gitlab grâce à une bibliothèque python.
Même si celle-ci n’est pas forcément toujours bien documentée, elle a permis un
gain de temps non négligeable dans la mesure où les objets pour représenter les
différents concepts de Gitlab existaient déjà (dépôts, utilisateurs).

Nous utilisons aussi le framework CSS Bootstrap, ce qui a facilité la compatibilité mobile.

## Route `signup`

### Partie utilisateur

Cette page permet à l’utilisateur d’entrer toutes les informations nécessaires
pour créer son compte et utiliser l’application. Nous avons choisi de ne pas
permettre à l’utilisateur qui vient de s’inscrire d’être directement connecté.

### Difficultés rencontrées

Il a fallu s’assurer que les utilisateurs ne cherchent pas à s’inscrire avec une adresse mail ou un nom d’utilisateur déjà existant. Il a donc fallu afficher un message d’erreur propre à chaque champ. En effet, pour des questions d’ergonomie, on ne peut pas seulement afficher à l’utilisateur que le formulaire est invalide utilisateur

# Route `signin`

### Partie utilisateur

Il s’agit d’une page classique d’identification. On rentre l’utilisateur et le mot de passe. Il y a une fonction se souvenir de moi.

### Difficultés rencontrées

Les mots de passe ont été hachés et salés, pour respecter les bonnes pratiques en matière de sécurité. Il a donc fallu vérifier le mot de passe avec précautions, en hachant le mot de passe et en passant le sel dans la fonction hmac.

# Route `statistiques`

<!-- TODO Fusionner avec Lucas -->


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

# Route : /stats/<int:numéro_dépot>

Cette page permet d'afficher un certain nombre de statistiques liées au dépot. On récupère ces statistiques à partir d'un fichier de sortie de gitinspector lancé sur un clone du dépot concerné. On en ressort: Un histogramme des changements par auteur et par semaine en terme d'ajout et de suppression, un camembert des responsabilités par ligne des changements sur la totalité du projet, un diagramme en barre de la part des changements en commentaire par auteur, et un tableau indiquant la responsabilité par ligne sur chaques fichiers par auteur.
Ces statistiques sont calculées uniquement pour le langage principal du dépot. Les autres langages sont ignorés.


## Route `/activity/<int:activity_id>`

La page **activity** permet de présenter ce que l'on appelle une activité dans l'application. Une activité est un regroupement de dépôts gits géré par le professeur responsable de cette activité (par exemple un TP ou un projet). Une fois qu'une activité est créée, il n'est plus possible de la modifier (une amélioration possible serait de permettre la modification d'une activité). Sur la page d'une activité, on peut accéder effectuer plusieurs actions :
- Accéder au dépôt qui a été fork pour créer les dépôts des élèves (le répertoire parent)
- Accéder aux dépôts de chacun des élèves ou groupes d'élèves selon le type d'activité
- Accéder aux statistiques des dépôts des élèves
- Créer une Merge Request d'une branche du dépôt parent sur les dépôts des élèves
- Créer des Issues sur une sélection de dépôts parmis les dépôts des étudiants

L'une des principales difficultés rencontrée pour l'élaboration de cette page est la création de la Merge Request sur les dépôts des élèves. En effet, l'API de Gitlab ne permet pas de répercuter une Merge Request qui a été faite sur le dépôt parent sur les dépôts créé avec le fork. Il faut donc pour chaque dépôt copier l'intégralité de la branche dont on souhaite faire une Merge Request dans une nouvelle branche qui porte le même nom si celle-ci n'existe pas déjà et la renomme si c'est le cas (on peut également noter qu'à partir d'un certain nombre de branches, l'API de gitlab ne permet pas de récupérer l'intégralité des branches d'un d'un dépôt et il devient donc impossible de vérifier que la branche n'existe pas déjà).
