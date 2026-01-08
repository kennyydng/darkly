# Survey - Parameter Tampering / Client-Side Validation Bypass

## Description de la faille

La page survey permet de voter pour différents sujets avec une note de 1 à 10. La validation est uniquement côté client (menu déroulant), permettant l'envoi de valeurs arbitraires.

## Vulnérabilités identifiées

### 1. Client-Side Validation Only

Le formulaire utilise un menu déroulant HTML pour restreindre les valeurs :
```html
<SELECT name="valeur" onChange='javascript:this.form.submit();'>
    <option value="1">1</option>
    ...
    <option value="10">10</option>
</SELECT>
```

**Problème** : Cette restriction existe uniquement dans le navigateur. Le serveur ne vérifie pas si la valeur reçue est réellement entre 1 et 10.

### 2. No Server-Side Validation

Le serveur accepte n'importe quelle valeur sans validation, permettant :
- Des valeurs négatives
- Des valeurs très grandes
- Des chaînes de caractères
- Tout type de donnée

### 3. Business Logic Bypass

L'envoi d'une valeur anormalement élevée déclenche une condition cachée qui révèle le flag.

## Exploitation

### Méthode

Utilisation de `curl` pour envoyer une requête POST avec une valeur modifiée :
```bash
curl -X POST "http://localhost:8080/?page=survey" \
  -d "sujet=2&valeur=2131" | grep "flag"
```

**Explication** :
- `sujet=2` : ID du sujet (valeur normale)
- `valeur=2131` : Note modifiée (au lieu de 1-10)

La valeur anormalement élevée fait exploser la moyenne et déclenche l'affichage du flag.

### Pourquoi ça fonctionne

1. Le menu déroulant est contourné en envoyant directement la requête HTTP
2. Le serveur ne valide pas la plage de valeurs acceptables
3. Une logique métier cachée révèle le flag quand la moyenne dépasse un seuil

## Solution de correction

### 1. Validation côté serveur (obligatoire)
```php
<?php
// Récupération des paramètres
$sujet = $_POST['sujet'];
$valeur = $_POST['valeur'];

// Validation des types
if (!is_numeric($valeur) || !is_numeric($sujet)) {
    http_response_code(400);
    die("Erreur : paramètres invalides");
}

// Validation des plages
if ($valeur < 1 || $valeur > 10) {
    http_response_code(400);
    die("Erreur : la valeur doit être entre 1 et 10");
}

if ($sujet < 1 || $sujet > 100) {
    http_response_code(400);
    die("Erreur : sujet invalide");
}

// Conversion sécurisée
$valeur = intval($valeur);
$sujet = intval($sujet);

// Traitement...
?>
```

### 2. Validation côté client (optionnel mais recommandé)

Conserver la validation côté client pour l'expérience utilisateur, mais **jamais comme seule protection**.
```html
<form onsubmit="return validateForm()">
    <select name="valeur" required>
        <option value="1">1</option>
        ...
        <option value="10">10</option>
    </select>
</form>

<script>
function validateForm() {
    const valeur = document.querySelector('[name="valeur"]').value;
    if (valeur < 1 || valeur > 10) {
        alert('Valeur invalide');
        return false;
    }
    return true;
}
</script>
```

### 3. Principe de défense en profondeur

- ✅ Validation côté client (UX)
- ✅ Validation côté serveur (sécurité)
- ✅ Prepared statements (si SQL)
- ✅ Logging des tentatives suspectes
- ✅ Rate limiting

### Règle d'or

> **Never trust user input**
> Toujours valider et assainir les données côté serveur, même si une validation côté client existe.

## Références

- OWASP: Input Validation
- OWASP: Client-Side Security Controls
- CWE-20: Improper Input Validation
- CWE-602: Client-Side Enforcement of Server-Side Security
