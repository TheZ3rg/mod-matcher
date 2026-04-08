from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QSplitter, QComboBox, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .widgets.mod_list_widget import ModListWidget
from .widgets.mod_info_widget import ModInfoWidget
from .widgets.version_info_widget import VersionInfoWidget
from .widgets.folder_selector_widget import FolderSelectorWidget

from core.minecraft_versions import MinecraftVersions
from core.folder_manager import FolderManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModMatcher")
        self.setMinimumSize(1000, 700)
        self.setWindowIcon(QIcon("src/resources/icons/icon.ico"))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 10)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        self.mod_list = ModListWidget()
        splitter.addWidget(self.mod_list)
        
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        
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
        self.versions_combobox = QComboBox()
        filters_layout.addWidget(self.versions_combobox)
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
        
        right_panel_layout.addWidget(top_section)
        
        # Информация о текущем моде
        self.mod_info = ModInfoWidget()
        right_panel_layout.addWidget(self.mod_info)
        
        # Виджет с информация о найденной версии
        self.version_info = VersionInfoWidget()
        right_panel_layout.addWidget(self.version_info)

        splitter.addWidget(right_panel)

        # Настройка размеров сплиттера
        splitter.setSizes([400, 600])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        self.load_minecraft_versions()
        
        self.folder_selector.backup_requested.connect(self.on_backup_requested)

    def on_backup_requested(self, source_folder: str, dest_folder: str):
        """Обработчик запроса на создание бэкапа"""
        FolderManager().backup_mods(self, source_folder, dest_folder)

    def load_minecraft_versions(self):
        """Загружает список версий Minecraft в комбобокс"""
        versions = MinecraftVersions().get_version_list()
        if versions:
            self.versions_combobox.addItems(versions)
