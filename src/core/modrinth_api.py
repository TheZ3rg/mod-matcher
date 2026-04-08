import requests
from typing import Optional, Dict, List


class ModrinthAPI:
    """Класс для работы с API Modrinth"""
    
    BASE_URL = "https://api.modrinth.com/v2"
    
    def get_version_by_hash(self, file_hash: str, hash_type: str = "sha1") -> Optional[Dict]:
        """
        Поиск версии мода по хешу файла
        Документация: https://docs.modrinth.com/api-spec/#tag/versions/operation/getVersionFromHash
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/version_file/{file_hash}",
                params={"hash": hash_type},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Ошибка поиска по хешу {file_hash}: {e}")
            return None
    
    def get_project_versions(self, project_id: str, 
                            loaders: List[str] = None, 
                            game_versions: List[str] = None) -> List[Dict]:
        """
        Получение списка версий проекта с фильтрацией
        """
        try:
            url = f"{self.BASE_URL}/project/{project_id}/version"
            params = {}
            
            if loaders:
                # Формат: ?loaders=["fabric","forge"]
                params["loaders"] = f'[{",".join(f'"{l}"' for l in loaders)}]'
            
            if game_versions:
                # Формат: ?game_versions=["1.20.1","1.20.4"]
                params["game_versions"] = f'[{",".join(f'"{v}"' for v in game_versions)}]'
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Ошибка получения версий для проекта {project_id}: {e}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Получение информации о проекте"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/project/{project_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка получения проекта: {e}")
            return None
    
    def search_projects(self, query: str, loaders: List[str] = None, 
                       game_versions: List[str] = None, limit: int = 5) -> List[Dict]:
        """Поиск проектов по названию"""
        try:
            params = {
                "query": query,
                "limit": limit
            }
            if loaders:
                params["facets"] = f'[["loader:{l}" for l in {loaders}]]'
            if game_versions:
                params["facets"] = f'[["versions:{v}" for v in {game_versions}]]'
            
            response = requests.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("hits", [])
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []
