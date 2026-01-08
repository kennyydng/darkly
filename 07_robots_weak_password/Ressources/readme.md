# Weak Password - Information Disclosure via robots.txt

## Description de la faille

Le fichier `robots.txt` révèle l'existence de répertoires sensibles qui ne devraient pas être publics. Le répertoire `/whatever` est accessible et contient un fichier `.htpasswd` téléchargeable contenant des identifiants hashés en MD5.

## Pourquoi chercher robots.txt ?

### Qu'est-ce que robots.txt ?

Le fichier `robots.txt` est un fichier standard placé à la racine d'un site web qui indique aux moteurs de recherche (Google, Bing, etc.) quelles pages ils peuvent ou ne peuvent pas explorer et indexer.

### Pourquoi c'est une cible en cybersécurité ?

1. **Toujours accessible** : Le fichier `robots.txt` est public par définition (accessible à `http://site.com/robots.txt`)
2. **Révèle la structure** : Les administrateurs y listent souvent des répertoires qu'ils veulent cacher des moteurs de recherche
3. **Fausse sécurité** : Beaucoup pensent que lister un répertoire dans `robots.txt` le "protège", mais ce fichier ne fait qu'indiquer aux robots de ne pas y aller - il ne bloque rien techniquement
4. **Carte au trésor** : Pour un attaquant, c'est une liste de chemins potentiellement intéressants à explorer

### Exemple typique
```
User-agent: *
Disallow: /admin
Disallow: /backup
Disallow: /config
```

Cela signifie : "Chers robots, merci de ne pas indexer ces répertoires". Mais un humain peut y accéder directement !

## Exploitation

### 1. Découverte du répertoire sensible

Accès au fichier `robots.txt` :
```
http://localhost:8080/robots.txt
```

Contenu :
```
User-agent: *
Disallow: /whatever
Disallow: /.hidden
```

### 2. Accès au répertoire

Accès direct au répertoire mentionné :
```
http://localhost:8080/whatever
```

Le listing de répertoire est activé, révélant le fichier `.htpasswd`.

### 3. Téléchargement du fichier sensible

Téléchargement de `.htpasswd` :
```
http://localhost:8080/whatever/.htpasswd
```

Contenu :
```
root:437394baff5aa33daa618be47b75cb49
```

### 4. Craquage du hash MD5

Le hash `437394baff5aa33daa618be47b75cb49` est identifié comme MD5.

Utilisation de CrackStation (https://crackstation.net/) :
```
Hash: 437394baff5aa33daa618be47b75cb49
Résultat: qwerty123@
```

### 5. Utilisation des identifiants

Accès à la zone protégée :
```
http://localhost:8080/admin
```

Authentification HTTP Basic :
- Username: `root`
- Password: `qwerty123@`

Résultat : Accès admin obtenu + flag

## Vulnérabilités identifiées

1. **Information Disclosure** : `robots.txt` révèle des chemins sensibles
2. **Directory Listing** : Le serveur liste le contenu du répertoire
3. **Sensitive Data Exposure** : Le fichier `.htpasswd` est accessible publiquement
4. **Weak Cryptographic Hash** : Utilisation de MD5 (obsolète et sans salt)
5. **Weak Password** : Mot de passe facilement craquable

## Solution de correction

### 1. Ne jamais lister de chemins sensibles dans robots.txt

**Mauvais :**
```
User-agent: *
Disallow: /admin
Disallow: /whatever
```

**Bon :**
```
User-agent: *
Disallow: /wp-admin/  # Uniquement des chemins publics mais non pertinents pour SEO
```

Les répertoires sensibles doivent être protégés par une vraie authentification, pas par obscurité.

### 2. Déplacer .htpasswd hors du répertoire web

**Structure correcte :**
```
/var/www/html/           ← Répertoire accessible par le web
/var/www/secure/         ← Répertoire NON accessible par le web
    .htpasswd            ← Placer le fichier ici
```

### 3. Utiliser bcrypt au lieu de MD5

Lors de la création du fichier `.htpasswd`, utiliser l'option `-B` pour bcrypt :
```bash
htpasswd -B -c /var/www/secure/.htpasswd root
```

Cela génère automatiquement un hash sécurisé au lieu de MD5.

## Références

- OWASP: Information Disclosure
- OWASP: Sensitive Data Exposure
- CWE-215: Information Exposure Through Debug Information
