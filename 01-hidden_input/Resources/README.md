# Hidden Input Field Manipulation

## La faille de sécurité

Ce challenge exploite une vulnérabilité courante : **l'utilisation de champs cachés (`hidden`) pour stocker des données sensibles**.

### Code vulnérable

```html
<form action="#" method="POST">
	<input type="hidden" name="mail" value="webmaster@borntosec.com" maxlength="15">
	<input type="submit" name="Submit" value="Submit">
</form>
```

## Pourquoi c'est une faille ?

Les champs `<input type="hidden">` **ne sont PAS une protection de sécurité** :

1. ✅ **Visible dans le code source** : Ctrl+U ou clic droit → "Afficher le code source"
2. ✅ **Modifiable avec les DevTools** : F12 permet d'éditer le HTML en temps réel
3. ✅ **Interceptable** : Les outils comme Burp Suite ou ZAP peuvent modifier les requêtes
4. ✅ **Contournable** : On peut recréer manuellement la requête HTTP

## Comment exploiter la faille

### Méthode 1 : DevTools du navigateur (la plus simple)

1. Ouvrir la page avec le formulaire
2. Appuyer sur **F12** pour ouvrir les DevTools
3. Aller dans l'onglet "Inspecteur" ou "Elements"
4. Localiser l'input caché :
   ```html
   <input type="hidden" name="mail" value="webmaster@borntosec.com">
   ```
5. **Double-cliquer sur la valeur** et la modifier
6. Essayer différentes valeurs : `admin@borntosec.com`, `root@borntosec.com`, etc.
7. Soumettre le formulaire

**Alternative** : Changer `type="hidden"` en `type="text"` pour rendre le champ visible et modifiable directement.

### Méthode 2 : Console JavaScript

Ouvrir la console (F12 → Console) et exécuter :

```javascript
document.querySelector('input[name="mail"]').value = "admin@borntosec.com";
document.querySelector('form').submit();
```

### Méthode 3 : cURL

```bash
curl -X POST http://[URL_DU_SITE]/ \
  -d "mail=admin@borntosec.com&Submit=Submit"
```

### Méthode 4 : Burp Suite / ZAP

1. Configurer le proxy pour intercepter les requêtes
2. Soumettre le formulaire normalement
3. Intercepter la requête POST
4. Modifier le paramètre `mail` dans la requête
5. Envoyer la requête modifiée

## Solution pour ce challenge

En testant différentes valeurs d'email (admin, root, etc.), le serveur révèle le flag lorsque la bonne adresse est utilisée.

**Flag obtenu** : `1d4855f7337c0c14b6f44946872c4eb33853f40b2d54393fbe94f49f1e19bbb0`

## Principe de sécurité violé

### Never Trust Client-Side Data

**Règle d'or** : Ne JAMAIS faire confiance aux données provenant du client.

Tout ce qui est côté client peut être manipulé :
- Champs `hidden`, `readonly`, `disabled`
- Validation JavaScript
- Cookies
- Headers HTTP
- Paramètres d'URL

## Comment se protéger ?

### ❌ Mauvaises pratiques

```html
<!-- N'IMPORTE QUI peut modifier cette valeur -->
<input type="hidden" name="isAdmin" value="false">
<input type="hidden" name="price" value="99.99">
<input type="hidden" name="userId" value="1234">
```

### ✅ Bonnes pratiques

1. **Validation côté serveur** : Toujours valider et vérifier les permissions sur le serveur
2. **Sessions serveur** : Stocker les informations sensibles dans des sessions côté serveur
3. **Tokens CSRF** : Protéger contre les attaques CSRF avec des tokens uniques
4. **Authentification forte** : Vérifier l'identité et les droits à chaque requête
5. **Principe du moindre privilège** : Ne jamais exposer plus d'informations que nécessaire

### Exemple sécurisé

```php
<?php
session_start();

// Vérifier que l'utilisateur est authentifié
if (!isset($_SESSION['user_id'])) {
    die('Non autorisé');
}

// Récupérer l'email depuis la SESSION, pas du formulaire
$email = $_SESSION['user_email'];

// Vérifier les permissions côté serveur
if (!hasPermission($_SESSION['user_id'], 'submit_form')) {
    die('Permission refusée');
}

// Traiter la requête de manière sécurisée
processForm($email);
?>
```

## Impact de la vulnérabilité

- **Élévation de privilèges** : Un utilisateur normal peut se faire passer pour un admin
- **Manipulation de prix** : Modifier le prix d'un produit avant l'achat
- **Accès non autorisé** : Accéder à des données d'autres utilisateurs
- **Bypass de restrictions** : Contourner des limites ou des validations

## Références

- OWASP Top 10 : A04:2021 – Insecure Design
- CWE-602: Client-Side Enforcement of Server-Side Security
- CWE-807: Reliance on Untrusted Inputs in a Security Decision
