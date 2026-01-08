# Cookie Manipulation - Insecure Authentication

## Description de la faille

Le site utilise un cookie `I_am_admin` pour déterminer si l'utilisateur est administrateur. La valeur du cookie est un hash MD5 d'un booléen (`true` ou `false`). Ce mécanisme d'authentification est facilement contournable car le cookie est contrôlé par le client et peut être modifié arbitrairement.

## Découverte

### Inspection des cookies

En ouvrant les DevTools (F12) > Application > Cookies > http://localhost:8080, on trouve un cookie :
```
Name: I_am_admin
Value: 68934a3e9455fa72420237eb05902327
```

### Analyse de la valeur

La valeur ressemble à un hash MD5 (32 caractères hexadécimaux).

**Décodage avec CrackStation (https://crackstation.net/) :**
```
Hash: 68934a3e9455fa72420237eb05902327
Résultat: false
```

Le cookie contient donc `MD5("false")`, indiquant que l'utilisateur n'est **pas** administrateur.

## Exploitation

### Génération du hash MD5 de "true"
```bash
echo -n "true" | md5sum
```

**Résultat :**
```
b326b5062b2f0e69046810717534cb09
```

### Modification du cookie

1. Ouvrir DevTools (F12)
2. Aller dans Application > Cookies
3. Double-cliquer sur la valeur du cookie `I_am_admin`
4. Remplacer par : `b326b5062b2f0e69046810717534cb09`
5. Recharger la page (F5)

### Résultat

Le site reconnaît l'utilisateur comme administrateur et révèle le flag.

## Vulnérabilités identifiées

### 1. Client-Side Security Control (CWE-602)

L'authentification repose entièrement sur un cookie contrôlé par le client. Le serveur fait confiance à cette donnée sans validation indépendante.

**Code vulnérable (hypothèse) :**
```php
<?php
$is_admin = $_COOKIE['I_am_admin'] ?? '';

if (md5('true') === $is_admin) {
    echo "Welcome Admin! Flag: ...";
} else {
    echo "Access denied";
}
?>
```

**Problème :** Le serveur vérifie le hash mais n'empêche pas l'utilisateur de le modifier.

### 2. Weak Cryptography (CWE-327)

MD5 est utilisé pour "protéger" le statut d'administrateur, mais :
- MD5 est réversible avec des rainbow tables
- Les seules valeurs possibles sont `MD5("true")` et `MD5("false")`
- Un hash seul ne protège pas contre la manipulation

### 3. Predictable Values (CWE-330)

Un attaquant peut facilement tester les deux seules valeurs possibles.

## Pourquoi c'est dangereux

Cette vulnérabilité permet :
- **Élévation de privilèges** : Un utilisateur normal obtient des droits administrateur
- **Contournement d'authentification** : Accès à des fonctionnalités réservées sans credentials
- **Accès non autorisé** : Consultation de données sensibles

## Solution de correction

### Utiliser des sessions côté serveur
```php
<?php
session_start();

// Après authentification réelle (login/password)
if (authenticate_user($username, $password)) {
    $_SESSION['user_id'] = $user_id;
    $_SESSION['is_admin'] = true;  // Stocké côté SERVEUR
}

// Vérification
if (!isset($_SESSION['is_admin']) || $_SESSION['is_admin'] !== true) {
    http_response_code(403);
    die("Access denied");
}

show_admin_panel();
?>
```

**Pourquoi c'est sécurisé :**
- Les données sont stockées côté serveur (pas dans le cookie)
- Le cookie contient seulement un ID de session aléatoire
- L'utilisateur ne peut pas modifier son statut admin

### Sécuriser les cookies
```php
<?php
setcookie(
    'session_id',
    $session_id,
    [
        'expires' => time() + 3600,
        'secure' => true,      // HTTPS uniquement
        'httponly' => true,    // Inaccessible en JavaScript
        'samesite' => 'Strict' // Protection CSRF
    ]
);
?>
```

## Références

- OWASP: Session Management Cheat Sheet
- OWASP: Broken Authentication
- CWE-602: Client-Side Enforcement of Server-Side Security
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
