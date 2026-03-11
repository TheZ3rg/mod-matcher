import requests
import re
from typing import Optional, Dict, List, Tuple
import urllib.parse


class ModrinthAPI:
    """Класс для работы с Modrinth API"""
    
    BASE_URL = "https://api.modrinth.com/v2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ModMatcher/1.0.0 (ваш email или контакт)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def search_mod(self, query: str) -> Optional[Dict]:
        """
        Поиск мода по названию
        Возвращает информацию о моде или None
        """
        try:
            # Кодируем запрос для корректной обработки Unicode
            encoded_query = urllib.parse.quote(query.encode('utf-8'))
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params={
                    "query": query,  # requests сам закодирует правильно
                    "limit": 5,
                    "index": "relevance"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("hits"):
                # Возвращаем первый найденный мод
                return data["hits"][0]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при поиске мода {query}: {e}")
            return None
        except Exception as e:
            print(f"Неизвестная ошибка при поиске мода {query}: {e}")
            return None
    
    def get_mod_versions(self, mod_id: str, game_version: str = None, loader: str = None) -> List[Dict]:
        """
        Получает список версий мода
        Можно фильтровать по версии игры и загрузчику
        """
        try:
            params = {}
            if game_version:
                params["game_versions"] = f'["{game_version}"]'
            if loader:
                # Приводим загрузчик к нижнему регистру и убираем лишнее
                loader_clean = loader.lower().split()[0] if loader else ""
                params["loaders"] = f'["{loader_clean}"]'
            
            response = self.session.get(
                f"{self.BASE_URL}/project/{mod_id}/version",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении версий мода {mod_id}: {e}")
            return []
        except Exception as e:
            print(f"Неизвестная ошибка при получении версий мода {mod_id}: {e}")
            return []
    
    def extract_mod_name_from_filename(self, filename: str) -> str:
        """
        Извлекает название мода из имени файла
        Убирает версию, даты и лишние символы
        """
        try:
            # Убираем расширение
            name = filename.rsplit('.', 1)[0]
            
            # Убираем версию в скобках или после дефиса
            patterns = [
                r'[-\s_]*(?:forge|fabric|quilt|neoforge)[-\s_]*',  # названия загрузчиков
                r'[-\s_]*mc\d+(?:\.\d+)*(?:\.\d+)?[-\s_]*',  # mc1.20.1
                r'[-\s_]*\d+\.\d+\.\d+(?:[-.]\w+)?[-\s_]*',  # 1.0.0, 1.0.0-beta
                r'[-\s_]*\d+\.\d+(?:\.\d+)?[-\s_]*',  # 1.0, 1.0.0
                r'[-\s_]*v\d+\.\d+\.\d+[-\s_]*',  # v1.0.0
                r'[-\s_]*\[\d+\.\d+\.\d+.*\][-\s_]*',  # [1.0.0]
                r'[-\s_]*\(\d+\.\d+\.\d+.*\)[-\s_]*',  # (1.0.0)
                r'[-\s_]*\d{4}-\d{2}-\d{2}[-\s_]*',  # -2024-01-01
                r'[-\s_]*universal[-\s_]*',  # universal
                r'[-\s_]*client[-\s_]*',  # client
                r'[-\s_]*server[-\s_]*',  # server
            ]
            
            for pattern in patterns:
                name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
            
            # Убираем лишние символы и пробелы
            name = re.sub(r'[_-]+', ' ', name)
            name = re.sub(r'\s+', ' ', name)
            name = name.strip(' -_')
            
            # Если имя стало пустым, возвращаем исходное (без расширения)
            if not name:
                name = filename.rsplit('.', 1)[0]
            
            return name
            
        except Exception as e:
            print(f"Ошибка при извлечении названия из {filename}: {e}")
            return filename.rsplit('.', 1)[0]
    
    def get_latest_version(self, mod_data: Dict, versions: List[Dict]) -> Optional[Dict]:
        """
        Определяет последнюю версию из списка
        """
        if not versions:
            return None
        
        try:
            # Сортируем по дате выпуска
            sorted_versions = sorted(
                versions,
                key=lambda v: v.get("date_published", ""),
                reverse=True
            )
            
            return sorted_versions[0] if sorted_versions else None
        except Exception as e:
            print(f"Ошибка при определении последней версии: {e}")
            return None
    
    def compare_versions(self, current_version: str, latest_version: str) -> bool:
        """
        Сравнивает версии
        Возвращает True если есть обновление
        """
        if not current_version or not latest_version:
            return False
        
        # Если версии совпадают - обновления нет
        if current_version == latest_version:
            return False
        
        # Простое сравнение строк
        # TODO: добавить семантическое сравнение версий
        return True
