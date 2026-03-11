from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor

from core.folder_manager import FolderManager


class ModListWidget(QWidget):
    """Виджет для отображения списка модов"""
    
    mod_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.folder_manager = FolderManager()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Список модов")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # Показываем заглушку
        self.show_placeholder()
    
    def show_placeholder(self):
        """Показывает заглушку, когда нет модов"""
        self.list_widget.clear()
        placeholder = QListWidgetItem("Выберите папку с модами")
        placeholder.setForeground(QColor("#7B7A7A"))
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsSelectable)
        self.list_widget.addItem(placeholder)
    
    def update_mod_list(self, folder_path):
        """Обновляет список модов из указанной папки"""
        self.list_widget.clear()
        
        mod_files = self.folder_manager.get_mod_files(folder_path)
        
        if not mod_files:
            self.show_placeholder()
            return
        
        for mod_name in mod_files:
            item = QListWidgetItem(mod_name)
            item.setForeground(QColor("#A5AE2E"))  # Черный цвет для реальных модов
            self.list_widget.addItem(item)
    
    def on_item_clicked(self, item):
        """Обработка клика по элементу списка"""
        # Игнорируем клик по заглушке
        if item.text() != "Выберите папку с модами":
            self.mod_selected.emit(item.text())
