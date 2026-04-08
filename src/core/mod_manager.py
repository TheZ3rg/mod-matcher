import os
import zipfile
import json
from typing import Dict, Optional
import tomllib
import hashlib
from core.modrinth_api import ModrinthAPI
import requests
from typing import Optional, Callable

class ModManager:
    """Класс для работы с метаданными модов"""
    
    def __init__(self):
        self.api = ModrinthAPI()
        self.current_folder_path = None

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Вычисляет SHA-1 хеш файла"""
        try:
            sha1_hash = hashlib.sha1()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha1_hash.update(chunk)
            return sha1_hash.hexdigest()
        except Exception as e:
            print(f"Ошибка вычисления хеша {file_path}: {e}")
            return None

    def check_for_updates(self, mod_filename: str, folder_path: str, 
                         minecraft_version: str, loader: str) -> Dict:
        """
        Проверяет наличие обновлений для мода
        Возвращает словарь с информацией о версии или None если обновлений нет
        """
        file_path = os.path.join(folder_path, mod_filename)
        
        # 1. Пробуем найти по SHA-1 хешу
        file_hash = self.calculate_file_hash(file_path)
        if file_hash:
            version_data = self.api.get_version_by_hash(file_hash)
            if version_data:
                # Нашли точное совпадение, проверяем обновления для конкретной версии Minecraft
                return self._check_newer_version_for_mc_version(
                    version_data, minecraft_version, loader
                )
        
        # 2. Если по хешу не нашли, пробуем извлечь имя мода из jar
        mod_info = self.get_mod_info_from_file(folder_path, mod_filename)
        if mod_info:
            # Ищем проекты по имени
            projects = self.api.search_projects(
                mod_info["name"],
                loaders=[loader.lower()],
                game_versions=[minecraft_version]
            )
            
            if projects:
                # Берем первый подходящий проект
                project_id = projects[0]["project_id"]
                # Получаем версии ТОЛЬКО для выбранной версии Minecraft
                versions = self.api.get_project_versions(
                    project_id,
                    loaders=[loader.lower()],
                    game_versions=[minecraft_version]
                )
                
                if versions:
                    # Сортируем по дате и берем последнюю версию ДЛЯ ЭТОЙ МАЙНКРАФТ ВЕРСИИ
                    latest_version = sorted(versions, 
                                          key=lambda x: x.get("date_published", ""), 
                                          reverse=True)[0]
                    
                    # Сравниваем с текущей версией
                    current_version = mod_info.get("version", "0")
                    if self._is_newer_version(latest_version["version_number"], current_version):
                        return self._prepare_version_info(latest_version, projects[0])
        
        return None
    
    def _check_newer_version_for_mc_version(self, current_version_data: Dict, 
                                            minecraft_version: str, loader: str) -> Optional[Dict]:
        """
        Проверяет, есть ли более новая версия для указанной версии Minecraft
        """
        project_id = current_version_data.get("project_id")
        if not project_id:
            return None
        
        # Получаем все версии для нужного загрузчика и КОНКРЕТНОЙ версии Minecraft
        versions = self.api.get_project_versions(
            project_id,
            loaders=[loader.lower()],
            game_versions=[minecraft_version]  # Только выбранная версия
        )
        
        if not versions:
            return None
        
        # Сортируем по дате (новые сверху)
        sorted_versions = sorted(versions, 
                                key=lambda x: x.get("date_published", ""), 
                                reverse=True)
        
        current_version_number = current_version_data.get("version_number", "0")
        current_version_id = current_version_data.get("id")
        
        # Ищем более новую версию для этой версии Minecraft
        for version in sorted_versions:
            # Пропускаем текущую версию
            if version.get("id") == current_version_id:
                continue
                
            if self._is_newer_version(version["version_number"], current_version_number):
                # Проверяем, что версия действительно поддерживает выбранный Minecraft
                game_versions = version.get("game_versions", [])
                if minecraft_version in game_versions:
                    # Получаем информацию о проекте
                    project = self.api.get_project(project_id)
                    return self._prepare_version_info(version, project)
        
        return None
    
    def _is_newer_version(self, new_version: str, current_version: str) -> bool:
        """Сравнивает версии (простое сравнение строк, можно улучшить)"""
        # Простое сравнение, для реального использования лучше использовать
        # библиотеку типа packaging.version
        return new_version != current_version
    
    def _prepare_version_info(self, version_data: Dict, project_data: Dict = None) -> Dict:
        """Подготавливает информацию о версии для отображения"""
        # Извлекаем зависимости, фильтруя None значения
        dependencies = []
        for dep in version_data.get("dependencies", []):
            if dep.get("dependency_type") == "required":
                version_id = dep.get("version_id")
                if version_id is not None:
                    dependencies.append(version_id)
                else:
                    # Если нет version_id, пробуем взять project_id
                    project_id = dep.get("project_id")
                    if project_id:
                        dependencies.append(f"project:{project_id}")
        
        # Извлекаем changelog
        changelog = version_data.get("changelog", "")
        if changelog and len(changelog) > 200:
            changelog = changelog[:200] + "..."
        
        # Получаем имя файла для отображения
        version_name = version_data.get("name") or version_data.get("version_number", "Unknown")
        
        return {
            "version_id": version_data.get("id"),
            "version_number": version_data.get("version_number"),
            "name": version_name,
            "changelog": changelog or "",
            "dependencies": dependencies,
            "download_urls": [f.get("url") for f in version_data.get("files", []) if f.get("url")],
            "project_id": version_data.get("project_id"),
            "project_title": project_data.get("title") if project_data else "",
            "date_published": version_data.get("date_published")
        }
    
    def get_mod_info_from_file(self, folder_path: str, mod_filename: str) -> Optional[Dict]:
        """
        Извлекает информацию о моде из jar файла
        Поддерживает:
        - Forge (новый): META-INF/mods.toml
        - Forge (старый): mcmod.info
        - Fabric/Quilt: fabric.mod.json
        """
        file_path = os.path.join(folder_path, mod_filename)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with zipfile.ZipFile(file_path, 'r') as jar_file:
                # 1. Пробуем Forge (новый) - mods.toml
                if 'META-INF/mods.toml' in jar_file.namelist():
                    with jar_file.open('META-INF/mods.toml') as info_file:
                        content = info_file.read().decode('utf-8')
                        data = tomllib.loads(content)
                        
                        mods_list = data.get('mods', [])
                        if mods_list and len(mods_list) > 0:
                            mod_data = mods_list[0]
                            return {
                                "name": mod_data.get("displayName", mod_filename),
                                "description": mod_data.get("description", "Нет описания"),
                                "version": mod_data.get("version", "Неизвестно"),
                                "minecraft_version": self._extract_mc_version_toml(data),
                                "author": self._extract_authors_toml(mod_data),
                                "loader": "Forge"
                            }
                
                # 2. Пробуем Forge (старый) - mcmod.info
                if 'mcmod.info' in jar_file.namelist():
                    with jar_file.open('mcmod.info') as info_file:
                        data = json.load(info_file)
                        
                        if isinstance(data, list) and len(data) > 0:
                            mod_data = data[0]
                        else:
                            mod_data = data
                        
                        return {
                            "name": mod_data.get("name", mod_filename),
                            "description": mod_data.get("description", "Нет описания"),
                            "version": mod_data.get("version", "Неизвестно"),
                            "minecraft_version": self._extract_mc_version_mcmodinfo(mod_data),
                            "author": self._extract_authors_json(mod_data),
                            "loader": "Forge"
                        }
                
                # 3. Пробуем Fabric/Quilt - fabric.mod.json
                if 'fabric.mod.json' in jar_file.namelist():
                    with jar_file.open('fabric.mod.json') as info_file:
                        data = json.load(info_file)
                        
                        authors = data.get("authors", [])
                        author_str = self._extract_authors_fabric(authors)
                        
                        return {
                            "name": data.get("name", mod_filename),
                            "description": data.get("description", "Нет описания"),
                            "version": data.get("version", "Неизвестно"),
                            "minecraft_version": self._extract_mc_version_fabric(data),
                            "author": author_str,
                            "loader": "Fabric"
                        }
                
                # Если файлы с метаданными не найдены
                return {
                    "name": mod_filename.replace(".jar", "").replace(".zip", ""),
                    "description": "Информация отсутствует",
                    "version": "Неизвестно",
                    "minecraft_version": "Неизвестно",
                    "author": "Неизвестно",
                    "loader": "Неизвестно"
                }
                
        except Exception as e:
            print(f"Ошибка чтения мода {mod_filename}: {e}")
            return {
                "name": mod_filename.replace(".jar", "").replace(".zip", ""),
                "description": f"Ошибка чтения: {str(e)}",
                "version": "Неизвестно",
                "minecraft_version": "Неизвестно",
                "author": "Неизвестно",
                "loader": "Неизвестно"
            }
    
    def _extract_mc_version_toml(self, data: dict) -> str:
        """Извлекает версию Minecraft из mods.toml"""
        # В mods.toml версия может быть в dependencies
        deps = data.get("dependencies", {})
        
        # Ищем зависимость от Minecraft
        for dep_name, dep_data in deps.items():
            if "minecraft" in dep_name.lower():
                version_range = dep_data.get("versionRange", "")
                return version_range if version_range else "Указана в зависимости"
        
        return "Не указана"
    
    def _extract_mc_version_mcmodinfo(self, mod_data: dict) -> str:
        """Извлекает версию Minecraft из mcmod.info"""
        # В старом формате может быть поле mcversion
        mc_version = mod_data.get("mcversion", "")
        if mc_version:
            return mc_version
        
        # Или в зависимости
        deps = mod_data.get("dependencies", [])
        for dep in deps:
            if isinstance(dep, dict) and "minecraft" in dep.get("modid", "").lower():
                return dep.get("version", "Указана в зависимости")
        
        return "Не указана"
    
    def _extract_mc_version_fabric(self, data: dict) -> str:
        """Извлекает версию Minecraft из fabric.mod.json"""
        # В fabric.mod.json версия указывается в depends
        depends = data.get("depends", {})
        
        # Ищем зависимость от Minecraft
        if "minecraft" in depends:
            version = depends["minecraft"]
            return version if version else "Указана в depends"
        
        # Или в recommends
        recommends = data.get("recommends", {})
        if "minecraft" in recommends:
            version = recommends["minecraft"]
            return version if version else "Указана в recommends"
        
        return "Не указана"
    
    def _extract_authors_toml(self, mod_data: dict) -> str:
        """Извлекает авторов из данных mods.toml"""
        authors = mod_data.get("authors", "")
        if not authors:
            return "Неизвестно"
        
        if isinstance(authors, list):
            return ", ".join(authors)
        return str(authors)
    
    def _extract_authors_json(self, mod_data: dict) -> str:
        """Извлекает авторов из mcmod.info"""
        authors = mod_data.get("authorList", mod_data.get("authors", []))
        if not authors:
            return mod_data.get("author", "Неизвестно")
        
        if isinstance(authors, list):
            return ", ".join(authors)
        return str(authors)
    
    def _extract_authors_fabric(self, authors) -> str:
        """Извлекает авторов из fabric.mod.json"""
        if not authors:
            return "Неизвестно"
        
        if isinstance(authors, list):
            author_names = []
            for a in authors:
                if isinstance(a, dict):
                    author_names.append(a.get("name", str(a)))
                else:
                    author_names.append(str(a))
            return ", ".join(author_names)
        return str(authors)
    
    def download_version(self, version_info: Dict, destination_folder: str, 
                        progress_callback: Callable[[int, int], None] = None) -> Optional[str]:
        """
        Скачивает версию мода в указанную папку
        Возвращает путь к сохраненному файлу или None при ошибке
        """
        if not version_info or not destination_folder:
            return None
        
        # Получаем URL для скачивания
        download_urls = version_info.get("download_urls", [])
        if not download_urls:
            print("Нет URL для скачивания")
            return None
        
        # Берем первый URL (обычно он один)
        download_url = download_urls[0]
        
        # Формируем имя файла
        version_number = version_info.get("version_number", "unknown")
        project_title = version_info.get("project_title", "mod")
        # Очищаем имя файла от недопустимых символов
        safe_title = "".join(c for c in project_title if c.isalnum() or c in " ._-")
        filename = f"{safe_title}-{version_number}.jar"
        file_path = os.path.join(destination_folder, filename)
        
        try:
            # Скачиваем файл с прогрессом
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
            
            return file_path
            
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return None
