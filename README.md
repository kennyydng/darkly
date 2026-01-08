# Darkly - Projet de Sécurité Web 42

## Description

Ce projet a pour but de découvrir la sécurité informatique dans le domaine du web. Il permet d'explorer **OWASP** (Open Web Application Security Project), le plus grand projet de sécurité web à ce jour, et de comprendre ce que beaucoup de frameworks font de manière automatique et transparente pour protéger les applications.

L'objectif est d'identifier et d'exploiter différentes vulnérabilités web sur une application intentionnellement vulnérable, puis de proposer des correctifs pour chaque faille découverte.

## Vulnérabilités Exploitées

Ce projet couvre 14 failles de sécurité web majeures :

### 1. Hidden Input Field Manipulation
**Dossier:** `01-forget_password_hidden_input/`  
Manipulation d'un champ caché dans un formulaire pour modifier l'email de récupération de mot de passe.

### 2. SQL Injection - Members Page
**Dossier:** `02-Members_SQL_Injection/`  
Injection SQL via le paramètre `id` pour extraire des données sensibles de la base de données.

### 3. Open Redirection
**Dossier:** `03-Open_redirection/`  
Exploitation d'une redirection non sécurisée dans les liens de réseaux sociaux pour révéler des informations sensibles.

### 4. XSS via Data URI
**Dossier:** `04-XSS_data_URI/`  
Cross-Site Scripting utilisant un schéma data URI dans les paramètres d'URL.

### 5. File Upload Sanitization Bypass
**Dossier:** `05-file_sanitize/`  
Contournement des filtres de validation pour uploader des fichiers malveillants.

### 6. Path Traversal (Directory Traversal)
**Dossier:** `06-path_traversal/`  
Exploitation du paramètre `page` pour accéder à des fichiers système via traversée de répertoires.

### 7. Robots.txt - Weak Password
**Dossier:** `07_robots_weak_password/`  
Découverte de répertoires cachés via robots.txt révélant des mots de passe faibles.

### 8. Robots.txt - Hidden Folders
**Dossier:** `08_robots_hidden_folders/`  
Exploration de dossiers cachés listés dans robots.txt pour trouver des informations sensibles.

### 9. Brute Force Attack
**Dossier:** `09_brute_force/`  
Attaque par force brute sur un formulaire de connexion sans protection contre les tentatives multiples.

### 10. Parameter Tampering - Survey
**Dossier:** `10_Survey_Parameter_tampering/`  
Manipulation de paramètres dans un formulaire de sondage pour contourner les validations côté client.

### 11. SQL Injection - Image Search
**Dossier:** `11_search_image_SQL_injection/`  
Injection SQL dans la fonctionnalité de recherche d'images pour extraire des données.

### 12. Header Spoofing
**Dossier:** `12_header_spoofing/`  
Manipulation des en-têtes HTTP pour contourner les contrôles de sécurité.

### 13. Cookie Manipulation
**Dossier:** `13_cookie_manipulation/`  
Modification des cookies pour élever ses privilèges ou accéder à des fonctionnalités réservées.

### 14. Stored XSS - Feedback
**Dossier:** `14_Stored_XSS_feedback/`  
Cross-Site Scripting persistant via le formulaire de feedback.

## Structure du Projet

Chaque vulnérabilité est documentée dans son propre dossier avec :
- `flag.txt` : Le flag obtenu après exploitation
- `Resources/README.md` : Documentation détaillée de la faille, son exploitation et les correctifs

## Technologies et Concepts Abordés

- **OWASP Top 10** : Les vulnérabilités web les plus critiques
- **Injection SQL** : Exploitation et prévention
- **XSS** (Cross-Site Scripting) : Réfléchi et stocké
- **Path Traversal** : Accès non autorisé aux fichiers système
- **Authentification et gestion de session** : Brute force, cookies
- **Validation des entrées** : Côté client vs côté serveur
- **Information Disclosure** : Fuites d'informations via robots.txt, redirections, etc.

## Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)