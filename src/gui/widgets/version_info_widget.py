from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QGroupBox, QPushButton)
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal


class VersionInfoWidget(QWidget):
    """Виджет с информацией о найденной версии"""

    NAME_PLACEHOLDER_TEXT = "Выберите мод для проверки"
    DEPS_PLACEHOLDER_TEXT = "Нет зависимостей"
    
    update_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.group_box = QGroupBox("Информация о новой версии", self)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.group_box)
        layout.setContentsMargins(0, 0, 0, 0)

        group_layout = QVBoxLayout(self.group_box)
        
        self.new_version_name = QLabel(self.NAME_PLACEHOLDER_TEXT)
        version_font = QFont()
        version_font.setBold(True)
        self.new_version_name.setFont(version_font)
        group_layout.addWidget(self.new_version_name)
        
        self.changelog = QLabel()
        self.changelog.setWordWrap(True)
        group_layout.addWidget(self.changelog)

        dependencies_layout = QHBoxLayout()
        dependencies_layout.addWidget(QLabel("Зависимости:"))
        # Будет отображать зависимости мода, полученные через api
        self.dependencies = QLabel(self.DEPS_PLACEHOLDER_TEXT)
        self.dependencies.setWordWrap(True)
        dependencies_layout.addWidget(self.dependencies)
        dependencies_layout.addStretch()
        group_layout.addLayout(dependencies_layout)
        
        # Кнопка обновления
        # Запускает процесс загрузки новой версии мода
        # Изначально неактивна, пока не выбран мод с доступным обновлением
        self.update_btn = QPushButton("Обновить")
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self._on_update_clicked)
        group_layout.addWidget(self.update_btn)
    
    def show_update_info(self, update_info: dict):
        """Отображает информацию о доступном обновлении"""
        version_name = update_info.get("name") or update_info.get("version_number", "Новая версия")
        self.new_version_name.setText(f"Доступно обновление: {version_name}")
        
        changelog = update_info.get("changelog", "")
        if changelog:
            self.changelog.setText(f"Что нового:\n{changelog}")
        else:
            self.changelog.setText("")
        
        # Обрабатываем зависимости, фильтруя None значения
        dependencies = update_info.get("dependencies", [])
        if dependencies:
            # Фильтруем None и пустые значения, преобразуем в строки
            valid_deps = [str(dep) for dep in dependencies if dep is not None and str(dep).strip()]
            if valid_deps:
                self.dependencies.setText(", ".join(valid_deps))
            else:
                self.dependencies.setText(self.DEPS_PLACEHOLDER_TEXT)
        else:
            self.dependencies.setText(self.DEPS_PLACEHOLDER_TEXT)
    
    def show_no_updates(self):
        """Показывает, что обновлений нет"""
        self.new_version_name.setText("Мод актуален")
        self.changelog.setText("")
        self.dependencies.setText(self.DEPS_PLACEHOLDER_TEXT)
    
    def reset(self):
        """Сбрасывает виджет в начальное состояние"""
        self.new_version_name.setText(self.NAME_PLACEHOLDER_TEXT)
        self.changelog.setText("")
        self.dependencies.setText(self.DEPS_PLACEHOLDER_TEXT)
        self.update_btn.setEnabled(False)

    def _on_update_clicked(self):
        """Обработчик клика по кнопке обновления"""
        self.update_requested.emit("update")
