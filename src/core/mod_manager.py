import os
from typing import Dict, List, Optional
from dataclasses import dataclass

from core.folder_manager import FolderManager
from core.modrinth_api import ModrinthAPI


@dataclass
class ModInfo:
    """Класс для хранения информации о моде"""
    filename: str
    display_name: str
    current_version: str = ""
    latest_version: str = ""
    has_update: bool = False
    mod_id: str = ""
    description: str = ""
    author: str = ""
    icon_url: str = ""
    versions: List[Dict] = None
    changelog: str = ""


class ModManager:
    """Класс для управления модами"""
    
    def __init__(self):
        self.folder_manager = FolderManager()
        self.api = ModrinthAPI()
        self.mods: Dict[str, ModInfo] = {}  # filename -> ModInfo
    
    def scan_folder(self, folder_path: str) -> List[str]:
        """Сканирует папку и возвращает список модов"""
        if not folder_path or not os.path.exists(folder_path):
            return []
        
        files = self.folder_manager.get_mod_files(folder_path)
        
        # Создаем записи для каждого мода
        for filename in files:
            if filename not in self.mods:
                display_name = self.api.extract_mod_name_from_filename(filename)
                self.mods[filename] = ModInfo(
                    filename=filename,
                    display_name=display_name,
                    current_version=self._extract_version_from_filename(filename)
                )
        
        return files
    
    def _extract_version_from_filename(self, filename: str) -> str:
        """Извлекает версию из имени файла"""
        import re
        
        # Ищем паттерны версий
        patterns = [
            r'(\d+\.\d+\.\d+(?:[-.]\w+)?)',  # 1.0.0, 1.0.0-beta
            r'(\d+\.\d+(?:\.\d+)?)',  # 1.0, 1.0.0
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return "Неизвестно"
    
    def check_for_updates(self, filename: str, game_version: str = None, loader: str = None) -> Optional[ModInfo]:
        """
        Проверяет наличие обновлений для конкретного мода
        """
        if filename not in self.mods:
            return None
        
        mod = self.mods[filename]
        
        # Ищем мод в API
        mod_data = self.api.search_mod(mod.display_name)
        if not mod_data:
            return mod
        
        # Сохраняем ID мода
        mod.mod_id = mod_data["project_id"]
        mod.description = mod_data.get("description", "")
        mod.author = mod_data.get("author", "")
        mod.icon_url = mod_data.get("icon_url", "")
        
        # Получаем версии
        versions = self.api.get_mod_versions(mod.mod_id, game_version, loader)
        mod.versions = versions
        
        # Определяем последнюю версию
        latest = self.api.get_latest_version(mod_data, versions)
        if latest:
            mod.latest_version = latest.get("version_number", "")
            mod.changelog = latest.get("changelog", "")
            
            # Сравниваем версии
            mod.has_update = self.api.compare_versions(
                mod.current_version,
                mod.latest_version
            )
        
        return mod
    
    def check_all_mods(self, game_version: str = None, loader: str = None) -> List[ModInfo]:
        """
        Проверяет обновления для всех модов
        """
        results = []
        for filename in list(self.mods.keys()):
            mod = self.check_for_updates(filename, game_version, loader)
            if mod:
                results.append(mod)
        
        return results
