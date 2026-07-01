"""
LinkedIn Profile Data Extractor using Unofficial API
Requires: python-linkedin or similar library
Note: LinkedIn's official API has strict limitations. For production, use OAuth2.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class LinkedInExtractor:
    """
    Extrae datos relevantes del perfil de LinkedIn.
    Los KPIs incluyen:
    - Años de experiencia total
    - Número de conexiones (proxy de red profesional)
    - Número de recomendaciones recibidas
    - Número de competencias endorsadas
    - Posiciones ocupadas
    """
    
    def __init__(self, profile_data: Dict):
        """
        Args:
            profile_data: Diccionario con datos del perfil descargados desde LinkedIn
        """
        self.data = profile_data
    
    @staticmethod
    def calculate_total_experience_years(experiences: List[Dict]) -> float:
        """
        Calcula años totales de experiencia a partir de la lista de puestos.
        
        Args:
            experiences: Lista de experiencias con startDate y endDate
            
        Returns:
            float: Años totales de experiencia
        """
        total_days = 0
        today = datetime.now()
        
        for exp in experiences:
            if not exp.get('startDate'):
                continue
                
            start = datetime.fromisoformat(str(exp['startDate']).replace('Z', '+00:00'))
            
            # Si no hay fecha de fin, usar hoy
            if exp.get('endDate'):
                end = datetime.fromisoformat(str(exp['endDate']).replace('Z', '+00:00'))
            else:
                end = today
            
            total_days += (end - start).days
        
        return round(total_days / 365.25, 2)
    
    @staticmethod
    def count_recommendations(profile_data: Dict) -> int:
        """
        Cuenta el número total de recomendaciones recibidas.
        
        Args:
            profile_data: Datos del perfil
            
        Returns:
            int: Número de recomendaciones
        """
        endorsements = profile_data.get('recommendations', {})
        return sum(len(v) for v in endorsements.values() if isinstance(v, list))
    
    @staticmethod
    def count_endorsements(profile_data: Dict) -> int:
        """
        Cuenta el total de skills con endorsements.
        
        Args:
            profile_data: Datos del perfil
            
        Returns:
            int: Número de skills endorsados
        """
        skills = profile_data.get('skills', [])
        return len([s for s in skills if s.get('endorsementCount', 0) > 0])
    
    @staticmethod
    def get_connection_count(profile_data: Dict) -> int:
        """
        Obtiene el número de conexiones (si está disponible).
        
        Args:
            profile_data: Datos del perfil
            
        Returns:
            int: Número de conexiones (500+ si dice "500+", estimado como 500)
        """
        connections = profile_data.get('connectionCount', 0)
        if isinstance(connections, str) and '+' in connections:
            return 500  # Valor conservador para "500+"
        return int(connections) if connections else 0
    
    @staticmethod
    def get_companies_worked(profile_data: Dict) -> int:
        """
        Cuenta el número de empresas donde ha trabajado.
        
        Args:
            profile_data: Datos del perfil
            
        Returns:
            int: Número de empresas
        """
        experiences = profile_data.get('experience', [])
        companies = set(exp.get('companyName', '') for exp in experiences)
        return len([c for c in companies if c])
    
    @staticmethod
    def get_positions_count(profile_data: Dict) -> int:
        """
        Cuenta el número total de posiciones ocupadas.
        
        Args:
            profile_data: Datos del perfil
            
        Returns:
            int: Número de puestos
        """
        return len(profile_data.get('experience', []))
    
    def extract_kpis(self) -> Dict:
        """
        Extrae todos los KPIs relevantes del perfil.
        
        Returns:
            Dict con los KPIs principales
        """
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
        """
        Calcula el porcentaje de completitud del perfil.
        
        Returns:
            int: Porcentaje (0-100)
        """
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
        """Convierte los KPIs a JSON."""
        return json.dumps(self.extract_kpis(), indent=2, ensure_ascii=False)


# Funciones helper para integración con el script principal
def load_linkedin_profile(file_path: str) -> Optional[Dict]:
    """
    Carga datos de LinkedIn desde un archivo JSON.
    
    Args:
        file_path: Ruta al archivo JSON con datos de LinkedIn
        
    Returns:
        Dict con los datos del perfil o None si no existe
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_path}")
        return None


if __name__ == "__main__":
    # Ejemplo de uso
    sample_data = {
        'experience': [
            {
                'companyName': 'Company A',
                'position': 'Data Analyst',
                'startDate': '2020-01-01',
                'endDate': '2021-06-30'
            }
        ],
        'skills': [
            {'skill': 'Python', 'endorsementCount': 15},
            {'skill': 'SQL', 'endorsementCount': 12}
        ],
        'recommendations': {
            'received': ['rec1', 'rec2', 'rec3']
        },
        'connectionCount': '500+'
    }
    
    extractor = LinkedInExtractor(sample_data)
    print(extractor.to_json())
