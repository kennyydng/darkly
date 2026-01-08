# Faille de Traversée de Répertoires (Path Traversal)

## Description

Cette vulnérabilité exploite le paramètre `page` qui est passé en méthode GET dans l'URL. Le site web utilise ce paramètre pour charger dynamiquement des pages, mais ne valide pas correctement les valeurs fournies.

## Exploit

Lorsqu'on navigue sur le site web, on peut observer la variable `page` dans l'URL en méthode GET. En testant avec d'autres valeurs comme `/` et `../../`, le site nous répond en nous trollant. 

L'astuce est de tester avec une séquence de traversée de répertoires pour remonter jusqu'à la racine du système et accéder à des fichiers sensibles :

```
x.x.x.x/?page=../../../../../../../../../../../etc/passwd
```

Cette requête nous permet d'accéder au fichier `/etc/passwd` du système et on obtient le flag :

```
b12c4b2cb8094750ae121a676269aa9e2872d07c06e429d25a63196ec1c8c1d0
```

## Explication Technique

La vulnérabilité de traversée de répertoires (également appelée "Path Traversal" ou "Directory Traversal") permet à un attaquant de lire des fichiers arbitraires sur le serveur en manipulant les chemins de fichiers.

- Les séquences `../` permettent de remonter dans l'arborescence des répertoires
- En enchaînant plusieurs `../`, on peut remonter jusqu'à la racine `/` du système
- Une fois à la racine, on peut accéder à n'importe quel fichier lisible comme `/etc/passwd`

## Solutions

Pour corriger cette faille de sécurité :

1. **Appliquer une whitelist** sur la variable `page` pour bloquer les caractères dangereux :
   - `.` (point)
   - `/` (slash)
   - `%` (encodage URL)

2. **Valider les entrées** : N'autoriser que des valeurs prédéfinies pour le paramètre `page`

3. **Pour les sites PHP** - Protection contre le RFI (Remote File Inclusion) :
   - Désactiver `allow_url_open` dans php.ini
   - Désactiver `allow_url_include` dans php.ini

4. **Utiliser des chemins absolus** ou un système de mapping pour éviter toute manipulation de chemin

## Impact

Cette vulnérabilité peut permettre à un attaquant de :
- Lire des fichiers de configuration contenant des mots de passe
- Accéder au code source de l'application
- Lire des fichiers système sensibles
- Dans certains cas, exécuter du code arbitraire (RFI)
