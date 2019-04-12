# Conventions

## Flask

### Spécifier les méthodes des routes (GET, POST)

``` py
@app.route('/login', methods=['GET', 'POST'])
```

## Messages à l’utilisateur

Pour afficher des bannières d’information, utiliser :

``` python
flash('Le groupe a bien été créé', 'success')
```

## Récupération d’éléments dans le formulaire

```
request.form.get('numberOfStudents')
```

où `numberOfStudents` est un attribut `name` du document HTML associé à la requête POST.

## Base de données

À l’insertion, si les champs ont des contraintes d’unicité, penser à vérifier
qu’on n’insère pas un enregistrement qui les viole.

Il faut donc faire une requête SQL pour vérifier qu’il n’existe pas de champs
en double alors qu’ils sont définis avec `unique=True`.

## Formattage

Pour les noms de variables, se référer à
[PEP8](https://pep8.org/#prescriptive-naming-conventions)
