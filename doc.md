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

# Route : /home/

Cette page regroupe les activités qui concernent un professeur connecté. Si un utilisateur non connecté essaye d'accéder cette page, il est redirigé sur l'accueil. On utilise la pagination pour naviguer dans les entrées du tableau. En backend sont faites des requêtes SQL pour la page concernée. Depuis cette page sont accessibles les les pages des activités grace aux liens situés à gauche de leurs entrées dans le tableau, et la page de création de groupe. 
