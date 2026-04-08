from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGroupBox)
from PySide6.QtGui import QFont

class ModInfoWidget(QWidget):
    """Виджет с информацией о текущем моде"""
    
    LABEL_PLACEHOLDER_TEXT = "Мод не выбран"
    DESCRIPTION_PLACEHOLDER_TEXT = "Выберите мод из списка слева"
    VERSIONS_PLACEHOLDER_TEXT = "—"
    AUTHOR_PLACEHOLDER_TEXT = "—"

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.group_box = QGroupBox("Текущая версия мода", self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.group_box)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group_layout = QVBoxLayout(self.group_box)
        
        self.mod_name = QLabel(self.LABEL_PLACEHOLDER_TEXT)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(16)
        self.mod_name.setFont(name_font)
        self.mod_name.setWordWrap(True)
        group_layout.addWidget(self.mod_name)
        
        self.description = QLabel(self.DESCRIPTION_PLACEHOLDER_TEXT)
        description_font = QFont()
        description_font.setBold(True)
        description_font.setPointSize(12)
        self.description.setFont(description_font)
        self.description.setWordWrap(True)
        group_layout.addWidget(self.description)

        versions_layout = QHBoxLayout()
        versions_layout.addWidget(QLabel("Текущая версия:"))
        self.versions = QLabel(self.VERSIONS_PLACEHOLDER_TEXT)
        versions_layout.addWidget(self.versions)
        versions_layout.addStretch()
        group_layout.addLayout(versions_layout)

        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Автор:"))
        self.author = QLabel(self.AUTHOR_PLACEHOLDER_TEXT)
        author_layout.addWidget(self.author)
        author_layout.addStretch()
        group_layout.addLayout(author_layout)
