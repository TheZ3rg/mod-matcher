from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import Signal

from core.folder_manager import FolderManager


class FolderSelectorWidget(QWidget):
    """Виджет для выбора папки с модами"""
    
    source_folder_changed = Signal(str)
    destination_folder_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.folder_manager = FolderManager()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Исходная папка
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
        
        # Папка назначения
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
        
        # Кнопка бэкапа
        backup_layout = QHBoxLayout()
        backup_layout.addStretch()
        self.backup_btn = QPushButton("💾 Создать бэкап модов")
        self.backup_btn.clicked.connect(self.create_backup)
        self.backup_btn.setEnabled(False)
        backup_layout.addWidget(self.backup_btn)
        main_layout.addLayout(backup_layout)
    
    def select_source_folder(self):
        """Выбор исходной папки с модами"""
        folder = self.folder_manager.select_folder(self, "Выберите папку с модами")
        if folder:
            self.source_path_edit.setText(folder)
            self.folder_manager.source_folder = folder
            self.source_folder_changed.emit(folder)
            # Включаем кнопку бэкапа, если выбраны обе папки
            self.update_backup_button_state()
    
    def select_dest_folder(self):
        """Выбор папки назначения"""
        folder = self.folder_manager.select_folder(self, "Выберите папку для сохранения обновлений")
        if folder:
            self.dest_path_edit.setText(folder)
            self.folder_manager.dest_folder = folder
            self.destination_folder_changed.emit(folder)
            # Включаем кнопку бэкапа, если выбраны обе папки
            self.update_backup_button_state()
    
    def update_backup_button_state(self):
        """Обновляет состояние кнопки бэкапа"""
        if self.source_path_edit.text() and self.dest_path_edit.text():
            self.backup_btn.setEnabled(True)
        else:
            self.backup_btn.setEnabled(False)
    
    def create_backup(self):
        """Создает бэкап модов"""
        self.folder_manager.backup_mods(
            self,
            self.source_path_edit.text(),
            self.dest_path_edit.text()
        )
