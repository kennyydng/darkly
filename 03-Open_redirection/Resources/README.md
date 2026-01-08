# Unsafe Redirection - Open Redirect & Information Disclosure

## 1. Découverte de la faille

Les liens des réseaux sociaux (footer) utilisent une redirection intermédiaire :
```
http://localhost:8080/index.php?page=redirect&site=facebook
```

Le paramètre `site` n'est pas validé → vulnérabilité exploitable.

## 2. Exploitation

### Obtenir le flag (Information Disclosure)

```bash
curl "http://localhost:8080/index.php?page=redirect&site=xyz"
```

L'application révèle le flag au lieu de gérer l'erreur :
```
Good Job Here is the flag : b9e775a0291fed784a2d9680fcfad7edd6b8cdf87648da647aaf4bba288bcab3
```

### Attaque par phishing (Open Redirect)

Le hacker crée un lien malveillant :
```
http://localhost:8080/index.php?page=redirect&site=https://fake-login.com
```

**Scénario :**
1. Il envoie ce lien par email/SMS
2. La victime voit le domaine légitime (`localhost:8080`) et fait confiance
3. Le site redirige vers le faux site du hacker
4. La victime entre ses credentials → le hacker les récupère


## 3. Risques

**Information Disclosure :**
- Révèle données sensibles (flags, stack traces, chemins système)
- Facilite la reconnaissance pour d'autres attaques

**Open Redirect :**
- Phishing : vol de credentials via faux sites
- Malware : redirection vers sites infectés
- Contournement de filtres de sécurité
- Confiance aveugle des utilisateurs au domaine légitime

## 4. Solution

### Validation par whitelist

```php
// ❌ Vulnérable
$site = $_GET['site'];
header("Location: https://" . $site . ".com");

// ✅ Sécurisé
$allowed_sites = [
    'facebook' => 'https://www.facebook.com/page',
    'twitter' => 'https://twitter.com/handle',
    'instagram' => 'https://www.instagram.com/profile'
];

$site = $_GET['site'] ?? '';

if (array_key_exists($site, $allowed_sites)) {
    header("Location: " . $allowed_sites[$site]);
    exit();
} else {
    header("HTTP/1.1 404 Not Found");
    exit();
}
```

### Gestion des erreurs

```php
// En production : désactiver l'affichage des erreurs
ini_set('display_errors', 0);
ini_set('log_errors', 1);
```

### Meilleure pratique

Supprimer la redirection intermédiaire et pointer directement vers les réseaux sociaux :

```html
<a href="https://www.facebook.com/page" target="_blank" rel="noopener noreferrer">
    <img src="facebook.png" alt="Facebook">
</a>
```

## Bonnes pratiques

1. **Whitelist** : Définir les valeurs autorisées explicitement
2. **Validation côté serveur** : Ne jamais faire confiance aux entrées utilisateur
3. **Logs sans exposition** : Enregistrer les erreurs sans les afficher
4. **Tests de sécurité** : Tester avec des valeurs invalides/malicieuses
