# Hidden Directory - Recursive File Discovery

## Description de la faille

Le fichier `robots.txt` révèle un répertoire `/.hidden` contenant une arborescence profonde de sous-répertoires. Un flag est caché dans l'un des nombreux fichiers README dispersés dans cette structure.

## Exploitation

### 1. Découverte du répertoire

Lecture de `robots.txt` révèle :
```
Disallow: /.hidden
```

### 2. Exploration du répertoire

Accès à `http://localhost:8080/.hidden/` révèle 26 sous-répertoires avec des noms aléatoires.

Chaque répertoire contient :
- D'autres sous-répertoires (structure récursive)
- Un fichier `README` avec des messages de diversion

### 3. Structure de l'arborescence
```
/.hidden/
├── amcbevgondgcrloowluziypjdh/
│   ├── README (message troll)
│   ├── acbnunauucfplzmaglkvqgswwn/
│   │   ├── README (message troll)
│   │   └── ...
│   └── ...
├── bnqupesbgvhbcwqhcuynjolwkm/
│   └── ...
└── ...
```

### 4. Script de recherche automatisée

Vu le nombre important de fichiers (plusieurs milliers), une recherche manuelle est impossible. Un script Python a été développé pour parcourir récursivement l'arborescence.

**Principe du script :**
1. Parcourir tous les répertoires récursivement
2. Lire chaque fichier README
3. Filtrer les messages de diversion (contenant "voisin", "aide", etc.)
4. Identifier le flag (format hexadécimal, >= 32 caractères)

### 5. Résultat

Flag trouvé à :
```
http://localhost:8080/.hidden/whtccjokayshttvxycsvykxcfm/igeemtxnvexvxezqwntmzjltkt/lmpanswobhwcozdqixbowvbrhw/README
```

Contenu :
```
Hey, here is your flag : d5eec3ec36cf80dce44a896f961c1831a05526ec215693c8f2c39543497d4466
```

## Vulnérabilités identifiées

1. **Information Disclosure** : Le fichier `robots.txt` expose le répertoire caché
2. **Directory Listing** : Le serveur permet la navigation dans l'arborescence
3. **Security by Obscurity** : La sécurité repose uniquement sur la complexité de l'arborescence, pas sur une vraie protection

## Solution de correction

### 1. Désactiver le directory listing

Configuration Apache (`.htaccess` ou configuration serveur) :
```apache
Options -Indexes
```

Résultat : L'utilisateur ne peut plus voir la liste des fichiers et répertoires.

### 2. Implémenter une vraie authentification

Si le répertoire contient des informations sensibles, utiliser une authentification :
```apache
<Directory "/var/www/html/.hidden">
    AuthType Basic
    AuthName "Restricted Area"
    AuthUserFile /var/www/secure/.htpasswd
    Require valid-user
</Directory>
```

### 3. Ne pas exposer de chemins sensibles dans robots.txt

Supprimer les références à des répertoires protégés dans `robots.txt`.

### 4. Permissions système

Définir les permissions correctes au niveau du système de fichiers :
```bash
chmod 700 /var/www/html/.hidden
```

Seul le propriétaire (serveur web) peut accéder au répertoire.

## Références

- OWASP: Information Disclosure
- OWASP: Directory Indexing
- CWE-548: Exposure of Information Through Directory Listing
```

---

## 📂 Structure de ton dossier pour cette faille
```
/hidden_directory/
├── flag
└── Resources/
    ├── README.md           (le fichier ci-dessus)
    └── find_flag.py        (ton script - optionnel pour la démo)
```

**Contenu du fichier `flag` :**
```
d5eec3ec36cf80dce44a896f961c1831a05526ec215693c8f2c39543497d4466
