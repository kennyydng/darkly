import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8080/.hidden/"
visited = set()

def get_links(url):
    """Récupère tous les liens d'une page de listing"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href not in ['../', '../']:
                links.append(href)

        return links
    except Exception as e:
        print(f"Erreur sur {url}: {e}")
        return []

def read_readme(url):
    """Lit le contenu d'un fichier README"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content = response.text.strip()

            # Liste de mots-clés pour identifier les messages de troll
            troll_keywords = [
                "veux de l'aide",
                "voisin",
                "droite",
                "gauche",
                "Moi aussi",
                "Toujours pas",
                "Non",
                "non"
            ]

            # Si le contenu est trop court (moins de 20 caractères) et contient un mot-clé troll
            if any(keyword.lower() in content.lower() for keyword in troll_keywords):
                return None

            # Si le contenu ressemble à un hash (longueur >= 32, caractères hexadécimaux)
            if len(content) >= 32 and all(c in '0123456789abcdefABCDEF\n\r ' for c in content):
                return content

            # Afficher les contenus suspects pour debug
            if len(content) > 10 and len(content) < 100:
                print(f"  → Contenu suspect ({len(content)} chars): {content[:50]}")
                return content

        return None
    except Exception as e:
        return None

def explore(url, depth=0):
    """Explore récursivement l'arborescence"""
    if url in visited:
        return None

    visited.add(url)
    # print(f"{'  ' * depth}Exploration: {url}")

    links = get_links(url)

    for link in links:
        full_url = urljoin(url, link)

        # Si c'est un fichier README
        if link == "README":
            content = read_readme(full_url)
            if content:
                print(f"\n{'='*60}")
                print(f"FLAG TROUVÉ À: {full_url}")
                print(f"Contenu: {content}")
                print(f"{'='*60}\n")
                return content

        # Si c'est un répertoire (se termine par /)
        elif link.endswith('/'):
            result = explore(full_url, depth + 1)
            if result:
                return result

    return None

if __name__ == "__main__":
    print("Début de la recherche du flag...\n")
    flag = explore(BASE_URL)

    if flag:
        print(f"\n✓ Flag trouvé: {flag}")
    else:
        print("\n✗ Aucun flag trouvé")
