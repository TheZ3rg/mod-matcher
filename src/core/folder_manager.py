import os
import zipfile
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QMessageBox


class FolderManager:
    """Класс для работы с файловой системой"""
    
    def select_folder(self, parent_widget, title="Выберите папку"):
        """Открывает диалог выбора папки и возвращает выбранный путь"""
        return QFileDialog.getExistingDirectory(parent_widget, title)
    
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
    
    def backup_mods(self, parent_widget, source_folder, dest_folder) -> bool:
        """
        Создает бэкап всех модов из source_folder в dest_folder
        Возвращает True если успешно
        """
        if not source_folder or not os.path.exists(source_folder):
            QMessageBox.warning(parent_widget, "Ошибка", "Исходная папка не выбрана или не существует")
            return False
        
        if not dest_folder or not os.path.exists(dest_folder):
            QMessageBox.warning(parent_widget, "Ошибка", "Папка назначения не выбрана или не существует")
            return False
        
        mod_files = self.get_mod_files(source_folder)
        
        if not mod_files:
            QMessageBox.information(parent_widget, "Информация", "Нет модов для бэкапа")
            return False
        
        # Создаем имя файла бэкапа с датой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"mods_backup_{timestamp}.zip"
        backup_path = os.path.join(dest_folder, backup_name)
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for mod_file in mod_files:
                    file_path = os.path.join(source_folder, mod_file)
                    zipf.write(file_path, mod_file)
            
            QMessageBox.information(
                parent_widget, 
                "Успешно", 
                f"Бэкап создан:\n{backup_path}\n\nСохранено модов: {len(mod_files)}"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Ошибка", f"Не удалось создать бэкап:\n{str(e)}")
            return False
