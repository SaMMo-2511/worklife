"""
LinkedIn Profile Data Extractor using public profile scraping (best-effort)
Requires: requests, beautifulsoup4
Note: LinkedIn public pages change often and may block scraping. This is a best-effort extractor
that parses visible HTML to retrieve experiences, education, skills, certifications, languages and
recommendations. For production use prefer LinkedIn official API (OAuth) or a maintained parser.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re


class LinkedInExtractor:
    """
    Extrae datos relevantes del perfil de LinkedIn a partir de un diccionario ya parseado.
    Los KPIs incluyen:
    - Años de experiencia total
    - Número de recomendaciones recibidas
    - Número de competencias endorsadas
    - Posiciones ocupadas
    """

    def __init__(self, profile_data: Dict):
        self.data = profile_data

    @staticmethod
    def calculate_total_experience_years(experiences: List[Dict]) -> float:
        total_days = 0
        today = datetime.now()

        for exp in experiences:
            if not exp.get('startDate'):
                continue

            try:
                start = datetime.fromisoformat(str(exp['startDate']).replace('Z', '+00:00'))
            except Exception:
                # try flexible parse YYYY or YYYY-MM formats
                try:
                    start = datetime(int(str(exp['startDate'])[:4]), 1, 1)
                except Exception:
                    continue

            if exp.get('endDate'):
                try:
                    end = datetime.fromisoformat(str(exp['endDate']).replace('Z', '+00:00'))
                except Exception:
                    try:
                        end = datetime(int(str(exp['endDate'])[:4]), 1, 1)
                    except Exception:
                        end = today
            else:
                end = today

            total_days += (end - start).days

        return round(total_days / 365.25, 2)

    @staticmethod
    def count_recommendations(profile_data: Dict) -> int:
        recs = profile_data.get('recommendations_received', [])
        return len(recs)

    @staticmethod
    def count_endorsements(profile_data: Dict) -> int:
        skills = profile_data.get('skills', [])
        return len([s for s in skills if s.get('endorsementCount', 0) > 0 or s.get('count', 0) > 0])

    @staticmethod
    def get_connection_count(profile_data: Dict) -> int:
        connections = profile_data.get('connectionCount', 0)
        if isinstance(connections, str) and '+' in connections:
            return 500
        try:
            return int(connections)
        except Exception:
            return 0

    @staticmethod
    def get_companies_worked(profile_data: Dict) -> int:
        experiences = profile_data.get('experience', [])
        companies = set(exp.get('companyName', '') for exp in experiences)
        return len([c for c in companies if c])

    @staticmethod
    def get_positions_count(profile_data: Dict) -> int:
        return len(profile_data.get('experience', []))

    def extract_kpis(self) -> Dict:
        experiences = self.data.get('experience', [])

        kpis = {
            'total_experience_years': self.calculate_total_experience_years(experiences),
            'companies_count': self.get_companies_worked(self.data),
            'positions_count': self.get_positions_count(self.data),
            'recommendations_count': self.count_recommendations(self.data),
            'endorsed_skills': self.count_endorsements(self.data),
            'connections': self.get_connection_count(self.data),
            'profile_completeness': self._calculate_profile_completeness(),
        }

        return kpis

    def _calculate_profile_completeness(self) -> int:
        completeness = 0
        checks = {
            'headline': 10,
            'about': 10,
            'experience': 20,
            'education': 15,
            'skills': 20,
            'recommendations': 10,
            'profilePhoto': 15,
        }

        for field, weight in checks.items():
            if field == 'profilePhoto':
                if self.data.get('profilePhoto') or self.data.get('profilePicture'):
                    completeness += weight
            elif field == 'experience':
                if len(self.data.get('experience', [])) > 0:
                    completeness += weight
            elif field == 'skills':
                if len(self.data.get('skills', [])) > 0:
                    completeness += weight
            elif field == 'recommendations':
                if self.count_recommendations(self.data) > 0:
                    completeness += weight
            elif self.data.get(field):
                completeness += weight

        return min(completeness, 100)

    def to_json(self) -> str:
        return json.dumps(self.extract_kpis(), indent=2, ensure_ascii=False)


# --- Helper para cargar desde JSON local ---
def load_linkedin_profile(file_path: str) -> Optional[Dict]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_path}")
        return None


# --- Best-effort: extraer datos públicos desde la URL del perfil ---
def fetch_public_profile(url: str, session: Optional[requests.Session] = None) -> Optional[Dict]:
    """
    Intenta descargar y parsear la información pública del perfil de LinkedIn indicada por `url`.
    Este extractor es heurístico y puede fallar si LinkedIn cambia su HTML o impone bloqueo.
    """
    s = session or requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }

    try:
        r = s.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"No se pudo descargar perfil: status {r.status_code}")
            return None

        soup = BeautifulSoup(r.text, 'html.parser')

        profile: Dict = {}

        # Nombre y titular
        name_tag = soup.find(['h1', 'h2'], string=True)
        if name_tag:
            profile['name'] = name_tag.get_text(strip=True)

        # Headline / titular
        head = soup.find('div', {'class': re.compile(r'headline|title|pv-top-card')})
        if head:
            txt = head.get_text(separator=' ', strip=True)
            profile['headline'] = txt

        # Experience blocks: buscar etiquetas que contengan "Experience" o listados de puestos
        experiences = []
        # LinkedIn public markup often has sections with id or aria-label
        exp_section = soup.find(lambda tag: tag.name in ['section', 'div'] and tag.get_text().lower().startswith('experience'))
        if not exp_section:
            # fallback: buscar elementos con 'experience' en el texto de su encabezado
            headers = soup.find_all(['h2', 'h3', 'h4'])
            for h in headers:
                if 'experience' in h.get_text(strip=True).lower():
                    # collect sibling list items
                    sib = h.find_next_sibling()
                    if sib:
                        exp_section = sib
                        break

        if exp_section:
            items = exp_section.find_all(lambda t: t.name in ['li', 'div'] and t.get_text(strip=True))
            for it in items[:20]:
                text = it.get_text(' | ', strip=True)
                # heuristics: split into position - company - dates
                parts = [p.strip() for p in text.split('|') if p.strip()]
                exp = {}
                if len(parts) >= 1:
                    exp['position'] = parts[0]
                if len(parts) >= 2:
                    exp['companyName'] = parts[1]
                # buscar años en el texto
                years = re.findall(r'(\d{4})', text)
                if years:
                    if len(years) == 1:
                        exp['startDate'] = years[0]
                    elif len(years) >= 2:
                        exp['startDate'] = years[0]
                        exp['endDate'] = years[1]
                experiences.append(exp)

        profile['experience'] = experiences

        # Education
        education = []
        edu_section = soup.find(lambda tag: tag.name in ['section', 'div'] and 'education' in (tag.get_text() or '').lower())
        if edu_section:
            edu_items = edu_section.find_all(['li', 'div'])
            for e in edu_items[:10]:
                t = e.get_text(' | ', strip=True)
                parts = [p.strip() for p in t.split('|') if p.strip()]
                if parts:
                    edu = {'institution': parts[0] if len(parts) == 1 else parts[1], 'title': parts[0] if len(parts) > 1 else '', 'year': ''}
                    years = re.findall(r'(\d{4})', t)
                    if years:
                        edu['year'] = f"{years[0]}-{years[-1]}" if len(years) > 1 else years[0]
                    education.append(edu)
        profile['education'] = education

        # Skills
        skills = []
        skill_nodes = soup.find_all(lambda tag: tag.name in ['span', 'li', 'div'] and tag.get_text() and len(tag.get_text(strip=True)) < 50 and re.search(r'\b(Skill|skills|Competencias|Habilidades)\b', tag.get_text(), re.I) is None)
        # crude heuristic: look for 'skill' lists by searching for common containers
        # Better heuristic: look for script tags with initialProfileData - skipped for simplicity
        # We'll fallback to empty skills
        profile['skills'] = skills

        # Certifications & Languages - best-effort: look for those section headings
        certs = []
        cert_section = soup.find(lambda tag: tag.name in ['section', 'div'] and 'certificat' in (tag.get_text() or '').lower())
        if cert_section:
            for c in cert_section.find_all(['li', 'div'])[:10]:
                txt = c.get_text(' | ', strip=True)
                certs.append({'title': txt})
        profile['certifications'] = certs

        langs = []
        lang_section = soup.find(lambda tag: tag.name in ['section', 'div'] and 'idioma' in (tag.get_text() or '').lower() or 'language' in (tag.get_text() or '').lower())
        if lang_section:
            for l in lang_section.find_all(['li', 'div'])[:10]:
                txt = l.get_text(' | ', strip=True)
                langs.append({'language': txt})
        profile['languages'] = langs

        # Recommendations - public profiles sometimes show snippets with author
        recs = []
        rec_section = soup.find(lambda tag: tag.name in ['section', 'div'] and 'recommend' in (tag.get_text() or '').lower())
        if rec_section:
            rec_items = rec_section.find_all(['li', 'div'])
            for r in rec_items[:10]:
                author = ''
                role = ''
                photo = None
                text = r.get_text(' | ', strip=True)
                # attempt to find author name inside
                name_tag = r.find(['h3', 'h4', 'h5', 'span'])
                if name_tag:
                    author = name_tag.get_text(strip=True)
                img = r.find('img')
                if img and img.get('src'):
                    photo = img.get('src')
                recs.append({'author': author, 'role': role, 'text': text, 'photo': photo})
        profile['recommendations_received'] = recs

        # Profile photo - try common selectors
        img = soup.find('img', {'class': re.compile(r'profile|pv-top-card__photo', re.I)})
        if img and img.get('src'):
            profile['profilePhoto'] = img.get('src')

        # Connection count - search for '500+' or 'conexiones'
        txt = soup.get_text()
        m = re.search(r'([0-9]{1,3}\+?)\s+connections|conexiones|connections', txt, re.I)
        if m:
            profile['connectionCount'] = m.group(1)

        return profile

    except Exception as e:
        print(f"Error extrayendo perfil público: {e}")
        return None


if __name__ == "__main__":
    # small test stub (non-exhaustive)
    url = "https://www.linkedin.com/in/samuel-moreno-moya-5a0a86210/"
    p = fetch_public_profile(url)
    if p:
        print(json.dumps(p, indent=2, ensure_ascii=False))
