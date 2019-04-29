# Gitly

## Développement

### Installer les dépendances

```
pip install -r requirements.txt
```

Pour ajouter des dépendances, il suffit de les référencer dans le fichier
[requirements.txt](./requirements.txt) et de relancer la commande ci-dessus.

### Lancer le serveur

```
FLASK_DEBUG=1 FLASK_APP=main.py flask run
```

## Release

### 0.1

- Les pages principales (création d’une nouvelle activité, formulaire de création d’un nouveau groupe d’élèves, pages d’accueil listant toutes les activités, page listant tous les dépôts d’une activité) ont leur partie front-end **uniquement** qui est achevée.
- Back-end fonctionnel : identification. L’identification fonctionne ( l’utilisateur peut s’inscrire, se connecter, se déconnecter). Les pages où l’utilisateur doit être identifié redirigent vers la page d’identification qui ramène à la page initiale.
- Par contre, les fonctions « Mot de passe oublié » et « Se souvenir de moi » ne sont pas achevées. 

### Documentation

Voir [la documentation](docs.md).
