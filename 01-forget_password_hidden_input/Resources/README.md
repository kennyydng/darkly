# Hidden Input Field Manipulation

## La faille

Le formulaire contient un champ caché avec une adresse email :

```html
<form action="#" method="POST">
	<input type="hidden" name="mail" value="webmaster@borntosec.com" maxlength="15">
	<input type="submit" name="Submit" value="Submit">
</form>
```

**Problème** : Les champs `type="hidden"` ne sont pas protégés. Ils sont simplement cachés visuellement mais restent modifiables.

## Solution

### Étapes pour obtenir le flag

1. Ouvrir les DevTools du navigateur (F12)
2. Aller dans l'onglet "Inspecteur" ou "Elements"
3. Trouver le champ caché `<input type="hidden" name="mail" value="webmaster@borntosec.com">`
4. Double-cliquer sur la valeur et la modifier en une autre adresse email
   - Par exemple : `admin@borntosec.com`, `root@borntosec.com`, etc.
5. Soumettre le formulaire modifié
6. **Le serveur retourne directement le flag !**

Le serveur accepte l'email modifié et révèle le flag car il fait confiance aux données envoyées par le client sans validation côté serveur.

**Alternative** : Changer `type="hidden"` en `type="text"` pour rendre le champ directement modifiable dans la page, puis modifier l'email et soumettre.

## Bonne pratique

### ❌ Ce qu'il ne faut PAS faire

```html
<!-- L'utilisateur peut modifier cette valeur ! -->
<input type="hidden" name="mail" value="webmaster@borntosec.com">
<input type="hidden" name="isAdmin" value="false">
```

### ✅ Solution sécurisée

**Ne jamais faire confiance aux données du client.** Stocker les informations sensibles côté serveur :

```php
<?php
session_start();

// Récupérer l'email depuis la SESSION, pas du formulaire
if (!isset($_SESSION['user_email'])) {
    die('Non autorisé');
}

$email = $_SESSION['user_email'];
// Traiter avec l'email de la session
?>
```

**Principe** : Tout ce qui vient du client (champs hidden, validation JavaScript, cookies) peut être manipulé. Toujours valider et autoriser côté serveur.
