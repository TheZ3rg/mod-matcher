from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGroupBox)
from PySide6.QtGui import QFont

class ModInfoWidget(QWidget):
    """Виджет с информацией о текущем моде"""
    
    LABEL_PLACEHOLDER_TEXT = "Мод не выбран"
    DESCRIPTION_PLACEHOLDER_TEXT = "Выберите мод из списка слева"
    VERSIONS_PLACEHOLDER_TEXT = "—"
    MINECRAFT_VERSION_PLACEHOLDER_TEXT = "—"
    AUTHOR_PLACEHOLDER_TEXT = "—"

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.group_box = QGroupBox("Информация о моде", self)
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

        # Версия мода
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Версия мода:"))
        self.version = QLabel(self.VERSIONS_PLACEHOLDER_TEXT)
        version_layout.addWidget(self.version)
        version_layout.addStretch()
        group_layout.addLayout(version_layout)

        # Версия Minecraft
        mc_version_layout = QHBoxLayout()
        mc_version_layout.addWidget(QLabel("Версия Minecraft:"))
        self.minecraft_version = QLabel(self.MINECRAFT_VERSION_PLACEHOLDER_TEXT)
        mc_version_layout.addWidget(self.minecraft_version)
        mc_version_layout.addStretch()
        group_layout.addLayout(mc_version_layout)

        # Автор
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Автор:"))
        self.author = QLabel(self.AUTHOR_PLACEHOLDER_TEXT)
        author_layout.addWidget(self.author)
        author_layout.addStretch()
        group_layout.addLayout(author_layout)
    
    def update_mod_info(self, name: str, description: str, version: str, minecraft_version: str, author: str):
        """Обновляет информацию о моде"""
        self.mod_name.setText(name)
        self.description.setText(description)
        self.version.setText(version)
        self.minecraft_version.setText(minecraft_version)
        self.author.setText(author)
    
    def show_not_found(self):
        """Показывает, что мод не найден"""
        self.mod_name.setText("Мод не найден")
        self.description.setText("Не удалось прочитать информацию о моде")
        self.version.setText("—")
        self.minecraft_version.setText("—")
        self.author.setText("—")
