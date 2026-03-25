import requests
from typing import List, Dict


class MinecraftVersions:
    """Класс для получения списка версий Minecraft"""
    
    MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    
    def __init__(self):
        self.versions: List[Dict] = []
        self.latest_release: str = ""
        self.latest_snapshot: str = ""
    
    def load_versions(self) -> bool:
        """Загружает данные о версиях от Mojang"""
        try:
            response = requests.get(self.MANIFEST_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.latest_release = data["latest"]["release"]
            self.latest_snapshot = data["latest"]["snapshot"]
            self.versions = data["versions"]
            return True
            
        except Exception as e:
            print(f"Ошибка получения версий: {e}")
            return False
    
    def get_version_list(self) -> List[str]:
        """Возвращает список ID стабильных версий для combobox"""
        if not self.versions:
            self.load_versions()

        return [v["id"] for v in self.versions if v["type"] == "release"]
