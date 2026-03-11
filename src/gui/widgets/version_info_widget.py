from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QGroupBox, QPushButton)
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal

from core.mod_manager import ModInfo


class VersionInfoWidget(QWidget):
    """Виджет с информацией о найденной версии"""
    
    update_requested = Signal(str)  # Сигнал для запроса обновления
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.group_box = QGroupBox("Информация о новой версии")
        group_layout = QVBoxLayout(self.group_box)
        
        self.new_version_label = QLabel("Выберите мод для проверки")
        version_font = QFont()
        version_font.setBold(True)
        self.new_version_label.setFont(version_font)
        group_layout.addWidget(self.new_version_label)
        
        self.changelog_label = QLabel()
        self.changelog_label.setWordWrap(True)
        group_layout.addWidget(self.changelog_label)
        
        # Кнопка обновления
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.update_btn = QPushButton("Обновить")
        self.update_btn.setEnabled(False)
        self.update_btn.setFixedWidth(100)
        self.update_btn.clicked.connect(self.on_update_clicked)
        button_layout.addWidget(self.update_btn)
        group_layout.addLayout(button_layout)

        main_layout.addWidget(self.group_box)
        
        self.current_mod = None
    
    def on_update_clicked(self):
        """Обработка нажатия на кнопку обновления"""
        if self.current_mod:
            self.update_requested.emit(self.current_mod.filename)
    
    def update_info(self, mod_info: ModInfo):
        """Обновляет информацию о версии"""
        self.current_mod = mod_info
        
        if mod_info.has_update:
            self.group_box.setTitle(f"Доступно обновление для {mod_info.display_name}")
            self.new_version_label.setText(
                f"Новая версия: {mod_info.latest_version} (текущая: {mod_info.current_version})"
            )
            
            if mod_info.changelog:
                self.changelog_label.setText(f"Что нового:\n{mod_info.changelog}")
            else:
                self.changelog_label.setText("Описание изменений недоступно")
            
            self.update_btn.setEnabled(True)
            self.update_btn.setText("Обновить")
        else:
            self.group_box.setTitle(f"Мод актуален")
            self.new_version_label.setText(
                f"Установлена последняя версия: {mod_info.current_version}"
            )
            self.changelog_label.setText("Обновлений не найдено")
            self.update_btn.setEnabled(False)
    
    def clear_info(self):
        """Очищает информацию"""
        self.current_mod = None
        self.group_box.setTitle("Информация о новой версии")
        self.new_version_label.setText("Выберите мод для проверки")
        self.changelog_label.setText("")
        self.update_btn.setEnabled(False)
