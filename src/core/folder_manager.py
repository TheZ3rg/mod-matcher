import os
from PySide6.QtWidgets import QFileDialog


class FolderManager:
    """Класс для работы с файловой системой"""
    
    def __init__(self):
        self.source_folder = ""
        self.dest_folder = ""
    
    def select_folder(self, parent_widget, title="Выберите папку"):
        """Открывает диалог выбора папки и возвращает выбранный путь"""
        folder = QFileDialog.getExistingDirectory(parent_widget, title)
        return folder
    
    def get_mod_files(self, folder_path):
        """Получает список .jar и .zip файлов в папке"""
        if not folder_path or not os.path.exists(folder_path):
            return []
        
        mod_files = []
        try:
            for file in os.listdir(folder_path):
                if file.endswith(('.jar', '.zip')):
                    mod_files.append(file)
        except Exception as e:
            print(f"Ошибка при чтении папки: {e}")
        
        return sorted(mod_files)
