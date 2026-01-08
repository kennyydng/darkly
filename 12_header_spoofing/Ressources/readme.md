# HTTP Header Spoofing - Referer and User-Agent Validation

## Description de la faille

Une page cachée accessible via l'URL `?page=b7e44c7a40c5f80139f0a50f3650fb2bd8d00b0d24667c4c2ca32c88e13b758f` vérifie les headers HTTP `Referer` et `User-Agent` avant de révéler le flag. Cette vérification côté serveur est facilement contournable en falsifiant ces headers.

## Découverte

### 1. Lien suspect dans le footer

Le footer de chaque page contient un lien vers une URL inhabituelle :
```html
<a href="?page=b7e44c7a40c5f80139f0a50f3650fb2bd8d00b0d24667c4c2ca32c88e13b758f">
    <li>&copy; BornToSec</li>
</a>
```

Le paramètre `page` contient un hash SHA-256 (64 caractères hexadécimaux), ce qui est suspect et suggère une page cachée.

### 2. Inspection de la page

En accédant à cette URL, une image d'albatros s'affiche. L'inspection du code source révèle des commentaires HTML :
```html
<!--
You must come from : "https://www.nsa.gov/".
-->

<!--
Let's use this browser : "ft_bornToSec". It will help you a lot.
-->
```

Ces commentaires indiquent que le serveur vérifie :
- Le **Referer** (d'où vient la requête)
- Le **User-Agent** (quel navigateur/client effectue la requête)

## Exploitation

### Qu'est-ce qu'on exploite ?

Le serveur fait confiance aux **headers HTTP** envoyés par le client. Ces headers peuvent être **facilement falsifiés** car ils sont contrôlés par le client, pas par le serveur.

### Les headers HTTP en question

#### 1. Referer Header
```
Referer: https://www.nsa.gov/
```

**Ce qu'il indique :** "Je viens de cette page"

**Utilisation légitime :** Quand tu cliques sur un lien, ton navigateur envoie automatiquement l'URL de la page d'origine dans le header `Referer`.

**Le problème :** Ce header est défini par le client et peut être modifié ou inventé. Le serveur ne peut pas vérifier si c'est vrai.

**Analogie :** C'est comme montrer une fausse carte de membre à l'entrée d'un club. Tu dis "Je viens du club VIP" mais personne ne vérifie.

#### 2. User-Agent Header
```
User-Agent: ft_bornToSec
```

**Ce qu'il indique :** "Je suis ce navigateur/logiciel"

**Utilisation légitime :** Permet au serveur de savoir quel navigateur tu utilises pour adapter le contenu (Chrome, Firefox, Safari, mobile, etc.).

**Le problème :** Tout comme le Referer, ce header est défini par le client et facilement modifiable.

**Analogie :** Tu peux prétendre être n'importe qui au téléphone, personne ne peut vérifier ton identité juste par ta voix.

### Code vulnérable côté serveur (hypothèse)
```php
<?php
$referer = $_SERVER['HTTP_REFERER'] ?? '';
$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';

if ($referer === 'https://www.nsa.gov/' && $user_agent === 'ft_bornToSec') {
    echo "Flag: f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188";
} else {
    echo "<img src='images/albatros.jpg'>";
}
?>
```

**Problème :** Le serveur fait confiance aux données envoyées par le client (`$_SERVER['HTTP_REFERER']` et `$_SERVER['HTTP_USER_AGENT']`) sans aucune validation indépendante.

### Commande d'exploitation
```bash
curl "http://localhost:8080/?page=b7e44c7a40c5f80139f0a50f3650fb2bd8d00b0d24667c4c2ca32c88e13b758f" \
  -H "Referer: https://www.nsa.gov/" \
  -H "User-Agent: ft_bornToSec"
```

**Explication de la commande :**

- `curl` : Outil en ligne de commande pour envoyer des requêtes HTTP
- `-H "Referer: https://www.nsa.gov/"` : Ajoute un header HTTP personnalisé qui prétend venir de nsa.gov
- `-H "User-Agent: ft_bornToSec"` : Ajoute un header HTTP qui prétend être le navigateur "ft_bornToSec"

**Ce qui se passe techniquement :**

1. Le client (curl) envoie une requête HTTP GET
2. La requête contient les headers falsifiés :
```
   GET /?page=b7e44c7a40c5f80139f0a50f3650fb2bd8d00b0d24667c4c2ca32c88e13b758f HTTP/1.1
   Host: localhost:8080
   Referer: https://www.nsa.gov/
   User-Agent: ft_bornToSec
```
3. Le serveur lit ces headers avec `$_SERVER['HTTP_REFERER']` et `$_SERVER['HTTP_USER_AGENT']`
4. Le serveur vérifie si les valeurs correspondent
5. Si oui → révèle le flag
6. Le serveur ne peut **pas** vérifier si ces headers sont authentiques

**Résultat :**
```html
<center><h2 style="margin-top:50px;">
The flag is : f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188
</h2></center>
```

**Flag obtenu :**
```
f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188
```

## Vulnérabilités identifiées

### 1. Client-Side Validation (CWE-602)

Le serveur fait confiance à des données contrôlées par le client (headers HTTP) sans aucune validation indépendante.

**Principe violé :** Never trust client input

### 2. Improper Authentication (CWE-287)

L'authentification repose sur des données facilement falsifiables (Referer et User-Agent) au lieu d'utiliser des mécanismes d'authentification robustes.

### 3. Security Through Obscurity

La "sécurité" repose sur :
- Une URL cachée (le hash SHA-256)
- Des vérifications de headers facilement contournables

Ce n'est **pas** une vraie sécurité.

## Pourquoi c'est dangereux

### Dans ce cas spécifique

Le flag est révélé en falsifiant simplement deux headers HTTP.

### Dans un contexte réel

Cette vulnérabilité pourrait permettre :

#### 1. Contournement de restrictions géographiques
```php
// Code vulnérable
if ($_SERVER['HTTP_REFERER'] === 'https://internal-network.com') {
    // Accès autorisé
}
```

Un attaquant externe peut prétendre venir du réseau interne.

#### 2. Contournement de paywalls

Certains sites offrent un accès gratuit si le Referer provient de certains partenaires (Google News, réseaux sociaux). Un attaquant peut falsifier le Referer pour accéder gratuitement au contenu payant.

#### 3. Bypass de sécurité basée sur User-Agent
```php
// Code vulnérable
if ($_SERVER['HTTP_USER_AGENT'] === 'AdminBot/1.0') {
    // Accès administrateur
}
```

#### 4. Tracking et analytics inexacts

Si un site se fie au Referer pour ses statistiques, un attaquant peut polluer les données.

## Solution de correction

### 1. Ne JAMAIS faire confiance aux headers HTTP pour la sécurité

**Règle d'or :** Les headers HTTP (Referer, User-Agent, etc.) peuvent être falsifiés et ne doivent **jamais** servir de mécanisme de sécurité ou d'authentification.

**Mauvais :**
```php
// ❌ Facilement contournable
if ($_SERVER['HTTP_REFERER'] === 'https://trusted-site.com') {
    grant_access();
}
```

**Bon :**
```php
// ✅ Authentification robuste
session_start();
if (isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true) {
    grant_access();
}
```

### 2. Utiliser une vraie authentification

Pour protéger du contenu sensible :
```php
<?php
session_start();

// Vérifier les credentials (login/password, JWT, OAuth, etc.)
if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    die("Unauthorized");
}

// L'utilisateur est authentifié de manière sécurisée
show_protected_content();
?>
```

### 3. Si vous devez utiliser ces headers (logs, analytics)

**Pour le logging et l'analyse uniquement, jamais pour la sécurité :**
```php
<?php
// OK pour des logs ou statistiques
$referer = $_SERVER['HTTP_REFERER'] ?? 'unknown';
$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'unknown';

// Loguer pour analytics (pas pour sécurité)
log_analytics($referer, $user_agent);

// Mais ne JAMAIS utiliser pour autorisation
if (user_is_authenticated_properly()) {
    grant_access();
}
?>
```

### 4. Supprimer la page cachée en production

Les pages de "test" ou "debug" ne doivent jamais exister en production.

### 5. Utiliser des tokens CSRF pour les actions sensibles

Pour les formulaires et actions importantes :
```php
<?php
session_start();

// Générer un token
if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// Vérifier le token
if ($_POST['csrf_token'] !== $_SESSION['csrf_token']) {
    die("Invalid token");
}
?>
```

## Références

- OWASP: Insecure Direct Object References
- CWE-602: Client-Side Enforcement of Server-Side Security
- CWE-287: Improper Authentication
- RFC 7231: HTTP Referer Header
