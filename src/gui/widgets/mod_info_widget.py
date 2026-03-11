from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGroupBox)
from PySide6.QtGui import QFont

class ModInfoWidget(QWidget):
    """Виджет с информацией о текущем моде"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        group_box = QGroupBox("Текущая версия мода")
        group_layout = QVBoxLayout(group_box)
        
        self.name_label = QLabel("Мод не выбран")
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(16)
        self.name_label.setFont(name_font)
        group_layout.addWidget(self.name_label)
        
        self.description_label = QLabel("Выберите мод из списка слева")
        description_font = QFont()
        description_font.setBold(True)
        description_font.setPointSize(12)
        self.description_label.setFont(description_font)
        self.description_label.setWordWrap(True)
        group_layout.addWidget(self.description_label)

        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Текущая версия:"))
        self.version_label = QLabel("—")
        version_layout.addWidget(self.version_label)
        version_layout.addStretch()
        group_layout.addLayout(version_layout)

        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Автор:"))
        self.author_label = QLabel("—")
        author_layout.addWidget(self.author_label)
        author_layout.addStretch()
        group_layout.addLayout(author_layout)

        main_layout.addWidget(group_box)
