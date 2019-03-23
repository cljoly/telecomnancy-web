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

Les fichiers seront actualisés à chaque fois qu’ils seront enregistrés.

### Documentation

- Pour utiliser Flask http://flask.pocoo.org/docs/1.0/quickstart/
- Pour dépolyer sur Google App Engine https://cloud.google.com/appengine/docs/standard/python3/quickstart
