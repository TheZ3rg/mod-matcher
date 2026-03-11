from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import Signal

from core.folder_manager import FolderManager


class FolderSelectorWidget(QWidget):
    """Виджет для выбора папки с модами"""
    
    # Новые сигналы для оповещения об изменении папок
    source_folder_changed = Signal(str)
    dest_folder_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Создаем менеджер папок
        self.folder_manager = FolderManager()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Первая строка - исходная папка
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Исходная папка:"))
        
        self.source_path_edit = QLineEdit()
        self.source_path_edit.setPlaceholderText("Выберите директорию с модами...")
        self.source_path_edit.setReadOnly(True)
        source_layout.addWidget(self.source_path_edit)
        
        self.source_browse_btn = QPushButton("Обзор...")
        self.source_browse_btn.clicked.connect(self.select_source_folder)
        source_layout.addWidget(self.source_browse_btn)
        
        main_layout.addLayout(source_layout)
        
        # Вторая строка - папка назначения
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Папка назначения:"))
        
        self.dest_path_edit = QLineEdit()
        self.dest_path_edit.setPlaceholderText("Выберите директорию для сохранения обновлений...")
        self.dest_path_edit.setReadOnly(True)
        dest_layout.addWidget(self.dest_path_edit)
        
        self.dest_browse_btn = QPushButton("Обзор...")
        self.dest_browse_btn.clicked.connect(self.select_dest_folder)
        dest_layout.addWidget(self.dest_browse_btn)
        
        main_layout.addLayout(dest_layout)
    
    def select_source_folder(self):
        """Выбор исходной папки с модами"""
        folder = self.folder_manager.select_folder(self, "Выберите папку с модами")
        if folder:
            self.source_path_edit.setText(folder)
            self.folder_manager.source_folder = folder
            self.source_folder_changed.emit(folder)
    
    def select_dest_folder(self):
        """Выбор папки назначения"""
        folder = self.folder_manager.select_folder(self, "Выберите папку для сохранения обновлений")
        if folder:
            self.dest_path_edit.setText(folder)
            self.folder_manager.dest_folder = folder
            self.dest_folder_changed.emit(folder)
