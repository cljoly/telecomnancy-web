# Gitly

## Développement

### Installer les dépendances

```
pip install -r requirements.txt
```

Pour ajouter des dépendances, il suffit de les référencer dans le fichier
[requirements.txt](./requirements.txt) et de relancer la commande ci-dessus.

Lancer le script de génération des fichiers nécessaires au statistiques :
```
./setup.sh
```

### Lancer le serveur

```
FLASK_DEBUG=1 FLASK_APP=main.py flask run
```

### Démonstration en ligne

Nous avons déployé en ligne sur une version gratuite du service Heroku. Il n’y
a donc pas de persistance des actions utilisateurs au delà de quelques heures.

https://pweb2019.herokuapp.com/

## Release

### 0.2

- Création de dépot avec l’API de Gitlab dans le cas de groupe d’un seul élève
  et dans le cas de groupes de plusieurs élèves.
  - Vérification systématique de la clé d’API à la connexion et sur chaque page
    où l’utilisateur est connecté (s’il est connecté, il peut potentiellement
    intéragir avec l’API Gitlab).
- Possibilité pour l’enseignant de mettre à jour un dépôt d’un ou plusieurs élèves,
  au travers d’une merge request.
- Les activités associés à un utilisateur sont affichées sur la page d’accueil.
  Il y a des liens pour aller vers l’activité.
- Déploiement sur Heroku d’une démonstration.
- Hachage des mots de passe dans la base de donnée, avec du sel pour éviter les
  attaques par dictionnaire.
- Correction d’un certain nombre de bugs et amélioration de l’esthétique
  générale de l’application (par exemple en ajoutant une image comme favicon et
  en la reprennant dans le menu)

### 0.1

- Les pages principales (création d’une nouvelle activité, formulaire de création d’un nouveau groupe d’élèves, pages d’accueil listant toutes les activités, page listant tous les dépôts d’une activité) ont leur partie front-end **uniquement** qui est achevée.
- Back-end fonctionnel : identification. L’identification fonctionne ( l’utilisateur peut s’inscrire, se connecter, se déconnecter). Les pages où l’utilisateur doit être identifié redirigent vers la page d’identification qui ramène à la page initiale.
- Par contre, les fonctions « Mot de passe oublié » et « Se souvenir de moi » ne sont pas achevées. 

### Documentation

Voir [la documentation](doc.md).
