from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QSplitter, QComboBox, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .widgets.mod_list_widget import ModListWidget
from .widgets.mod_info_widget import ModInfoWidget
from .widgets.version_info_widget import VersionInfoWidget
from .widgets.folder_selector_widget import FolderSelectorWidget

from core.mod_manager import ModManager

from core.minecraft_versions import MinecraftVersions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModMatcher")
        self.setMinimumSize(1000, 700)
        self.setWindowIcon(QIcon("mod-matcher/src/resources/icons/icon.ico"))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        self.mod_list = ModListWidget()
        splitter.addWidget(self.mod_list)
        
        # Правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя секция - выбор директории и фильтры
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Выбор директорий
        self.folder_selector = FolderSelectorWidget()
        top_layout.addWidget(self.folder_selector)

        # Фильтры (версия, API, загрузчик)
        filters_widget = QWidget()
        filters_layout = QHBoxLayout(filters_widget)
        filters_layout.setContentsMargins(20, 0, 20, 0)
        
        # Версия Minecraft
        filters_layout.addWidget(QLabel("Версия:"))
        self.version_combo = QComboBox()
        filters_layout.addWidget(self.version_combo)
        filters_layout.addStretch(1)
        
        # API/Платформа
        filters_layout.addWidget(QLabel("API:"))
        self.api_combo = QComboBox()
        self.api_combo.addItems(["Modrinth", "CurseForge"])
        filters_layout.addWidget(self.api_combo)
        filters_layout.addStretch(1)
        
        # Загрузчик
        filters_layout.addWidget(QLabel("Загрузчик:"))
        self.loader_combo = QComboBox()
        self.loader_combo.addItems(["Forge", "Fabric", "Quilt", "NeoForge"])
        filters_layout.addWidget(self.loader_combo)
        
        top_layout.addWidget(filters_widget)
        
        right_layout.addWidget(top_section)
        
        # Информация о текущем моде
        self.mod_info = ModInfoWidget()
        right_layout.addWidget(self.mod_info)
        
        # Информация о найденной версии
        self.version_info = VersionInfoWidget()
        right_layout.addWidget(self.version_info)

        splitter.addWidget(right_panel)

        splitter.setSizes([400, 600])

        self.mod_manager = ModManager()
        self.version_manager = MinecraftVersions()
        self.load_minecraft_versions()

        self.version_info.update_requested.connect(self.on_update_requested)
        self.mod_list.mod_selected.connect(self.on_mod_selected)
        self.folder_selector.source_folder_changed.connect(self.on_source_folder_changed)

    def on_mod_selected(self, mod_name):
        """Обработка выбора мода"""
        # Получаем информацию о моде из менеджера
        mod_info = self.mod_manager.mods.get(mod_name)
        
        if mod_info:
            self.mod_info.name_label.setText(mod_info.display_name)
            self.mod_info.description_label.setText(mod_info.description or "Описание отсутствует")
            self.mod_info.version_label.setText(mod_info.current_version)
            self.mod_info.author_label.setText(mod_info.author or "Неизвестный автор")
            
            # Проверяем обновления
            game_version = self.version_combo.currentText()
            loader = self.loader_combo.currentText()
            
            updated_mod = self.mod_manager.check_for_updates(
                mod_name, 
                game_version, 
                loader
            )
            
            if updated_mod:
                self.version_info.update_info(updated_mod)
        else:
            # Если мод не найден в менеджере, показываем базовую информацию
            self.mod_info.name_label.setText(mod_name)
            self.mod_info.description_label.setText("Информация загружается...")
            self.mod_info.version_label.setText("—")
            self.mod_info.author_label.setText("—")
            self.version_info.clear_info()

    def on_source_folder_changed(self, folder_path):
        """Обработка изменения исходной папки"""
        print(f"Выбрана папка: {folder_path}")
        
        # Сканируем папку и обновляем список
        files = self.mod_manager.scan_folder(folder_path)
        self.mod_list.update_mod_list(folder_path)
        
        # Если есть моды, выбираем первый для отображения
        if files and len(files) > 0:
            self.mod_list.list_widget.setCurrentRow(0)
            self.on_mod_selected(files[0])

    def on_update_requested(self, filename):
        """Обработка запроса на обновление"""
        print(f"Запрошено обновление для: {filename}")
        # Здесь будет логика скачивания обновления

    def load_minecraft_versions(self):
        """Загружает список версий Minecraft в комбобокс"""

        versions = self.version_manager.get_version_list()
    
        if versions:
            self.version_combo.addItems(versions)
