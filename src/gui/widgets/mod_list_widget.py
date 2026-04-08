from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor

from core.folder_manager import FolderManager


class ModListWidget(QWidget):
    """Виджет для отображения списка модов"""
    
    PLACEHOLDER_TEXT = "Выберите папку с модами"

    mod_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Список модов")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)

        self.mod_list = QListWidget()
        self.mod_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.mod_list)

        self.show_placeholder()
    
    def show_placeholder(self):
        """Показывает подсказку, когда не выбрана директория с модами"""
        self.mod_list.clear()
        placeholder = QListWidgetItem(self.PLACEHOLDER_TEXT)
        placeholder.setForeground(QColor("#7B7A7A"))
        # Отключаем возможность выбирать подсказку как элемент списка
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsSelectable)
        self.mod_list.addItem(placeholder)
    
    def update_mod_list(self, folder_path):
        """Обновляет список модов из указанной папки"""
        self.mod_list.clear()
        
        mod_files = FolderManager().get_mod_files(folder_path)
        
        if not mod_files:
            self.show_placeholder()
            return
        
        # Блокируем обновления листа,
        # чтобы не вызывать зависания при большом количестве модов
        self.mod_list.setUpdatesEnabled(False)
        
        for mod_name in mod_files:
            item = QListWidgetItem(mod_name)
            item.setForeground(QColor("#A5AE2E"))
            self.mod_list.addItem(item)

        self.mod_list.setUpdatesEnabled(True)
    
    def on_item_clicked(self, item):
        """Обработка клика по элементу списка"""
        # Игнорируем клик по заглушке
        if item.text() != self.PLACEHOLDER_TEXT:
            self.mod_selected.emit(item.text())
