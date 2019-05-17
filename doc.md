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

# Pagination

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

# Route : /home/

Cette page regroupe les activités qui concernent un professeur connecté. Si un utilisateur non connecté essaye d'accéder cette page, il est redirigé sur l'accueil. On utilise la pagination pour naviguer dans les entrées du tableau. En backend sont faites des requêtes SQL pour la page concernée. Depuis cette page sont accessibles les les pages des activités grace aux liens situés à gauche de leurs entrées dans le tableau, et la page de création de groupe. 

## Route : /home/newactivity

Cette page n'est accessible que si l'utilisateur est connecté et que sa clé d'API est valide. Elle permet de créer une nouvelle activité. Il faut alors entrer : 
 - son nom,
 - ses dates de début et de fin,
 - le module associé : il est possible de choisir soit dans la liste des modules déjà existants, soit de créer un nouveau module en renseignant le nom long et le nom abrégé. L'affichage est intelligent, cela affiche le volet des modules existants s'il en existe au moins un, sinon cela affiche le volet de création d'un nouveau module.
 - l'enseignant référent : la liste des enseignants existants est affichée sous la forme d'une liste. Il suffit alors de cliquer sur l'enseignant que l'on souhaite affecter comme référent.
 - le nombre d'étudiants par groupe de l'activité : il s'agit ici de déterminer la cardinalité des groupes qui seront composés pour l'activité. Par exemple, si on choisit "un étudiant", chaque groupe ne sera composé que d'un élève, il y aura alors un dépôt par élève qui sera créé. Ce cas est idéal dans la création de TPs. Dans le cas des groupes avec plusieurs élèves, on peut choisir entre deux et six élèves. 
 - les élèves qui participeront à l'activité : il faut pour cela choisir un fichier au format CSV, ne comprenant pas d'entête et  contenant les champs suivants :
 
    | Nom | Prénom | Adresse mail | Nom d'utilisateur Gitlab |
    |-----|--------|--------------|--------------------------|

    Tous les élèves alors présents dans le fichier CSV sont chargés dans la colonne "Étudiants disponibles". Pour sélectionner plusieurs étudiants dans la liste, il suffit de garder la touche `CTRL` enfoncée et cliquer sur les étudiants désirés. Il faut alors déplacer les étudiants que l'on souhaite ajouter à l'activité dans la colonne "Étudiants de l'activité".Pour cela quatre flèches sont disponibles :
        - **&larr;** et **&rarr;** : Permet de déplacer les étudiants sélectionnés d'une colonne à l'autre. 
        - **>** et **<** : Permet de déplacer tous les étudiants d'une colonne vers l'autre.
    
 Pour valider la création de l'activité il faut cliquer ensuite sur le bouton "Créer l'activité" :
 - Le dépot sur Gitlab de l'activité est créé 
  - Lorsqu'on créé des groupes avec un élève : pour tous les élèves renseignés, un nouveau dépôt est créé en effectuant un fork du dépôt de l'activité. 
 - Lorsqu'on crée des groupes avec plusieurs élèves : un lien est envoyé par mail à tous les étudiants renseignés afin qu'il créent leur groupe. Ce lien est unique pour une activité.

## Route : '/newactivity/form/<form_number>'

Cette route affiche la page d'un formulaire de création de groupe pour les groupes comptant plus d'un élève. Elle est accessible pour toute personne disposant du lien (qui doit normalement avoir été reçu par mail pour les élèves concernés). Il n'y a pas besoin d'être connecté pour pouvoir accéder à cette page. Les élèves doivent alors renseigner :
 - Le nom de leur groupe
 - Le nom d'utilisateur Gitlab de chacun des membres du groupe
 
 Pour valider la création du groupe, il faut cliquer sur le bouton "Créer le groupe". Un dépôt sera alors créé via un fork du dépôt de l'activité, et en ajoutant tous les élèves en tant que "Développeur". Si un des noms d'utilisateur n'existe pas, le dépôt ne sera pas créé. 
 
 ## Route : '/forgottenPassword'
 
 Cette page permet de rentrer son adresse mail afin de réinitialiser son mot de passe. Une erreur sera affichée si aucun compte ne correspond à l'adresse mail renseignée. Si l'adresse est valable, un email est envoyé contenant un lien de réinitialisation du mot de passe. Le lien n'est valable que pour l'adresse mail renseignée et ceci pour une durée de 24 heures pour des raisons de sécurité. Si l'utilisateur demande une nouvelle fois à réinitialiser son mot de passe alors qu'un lien est toujours valable, ce même lien sera renvoyé. 
 
 ## Route : '/reset_password/<hash_url>'
 
 Cette page n'est accessible que depuis un lien de réinitialisation de mot de passe reçu par mail et seulement si ce lien est toujours valide. 
 <!-- TODO : continuer -->