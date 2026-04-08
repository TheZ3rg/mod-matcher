from PySide6.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QAbstractItemView, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor

from core.folder_manager import FolderManager


class ModListWidget(QWidget):
    """Виджет для отображения списка модов"""
    
    PLACEHOLDER_TEXT = "Выберите папку с модами"

    mod_selected = Signal(str)
    mods_selection_changed = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель с кнопками
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 5)
        
        title = QLabel("Список модов")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        # Кнопка "Выбрать все"
        self.select_all_btn = QPushButton("Выбрать все")
        self.select_all_btn.setMaximumWidth(100)
        self.select_all_btn.clicked.connect(self.select_all)
        top_layout.addWidget(self.select_all_btn)
        
        # Кнопка "Снять выделение"
        self.clear_selection_btn = QPushButton("Снять всё")
        self.clear_selection_btn.setMaximumWidth(100)
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        top_layout.addWidget(self.clear_selection_btn)
        
        layout.addWidget(top_panel)

        self.mod_list = QListWidget()
        # Включаем множественный выбор
        self.mod_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.mod_list.itemClicked.connect(self.on_item_clicked)
        self.mod_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.mod_list)

        self.show_placeholder()
    
    def show_placeholder(self):
        """Показывает подсказку, когда не выбрана директория с модами"""
        self.mod_list.clear()
        self.select_all_btn.setEnabled(False)
        self.clear_selection_btn.setEnabled(False)
        
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
            self.select_all_btn.setEnabled(False)
            self.clear_selection_btn.setEnabled(False)
            return
        
        # Включаем кнопки выбора
        self.select_all_btn.setEnabled(True)
        self.clear_selection_btn.setEnabled(True)
        
        # Блокируем обновления листа
        self.mod_list.setUpdatesEnabled(False)
        
        for mod_name in mod_files:
            item = QListWidgetItem(mod_name)
            # По умолчанию серый цвет (не проверен)
            item.setForeground(QColor("#888888"))
            self.mod_list.addItem(item)

        self.mod_list.setUpdatesEnabled(True)
    
    def update_mod_status(self, mod_name: str, status: str):
        """
        Обновляет цвет мода в списке
        status: 'has_update' (зеленый), 'not_found' (красный), 'up_to_date' (желтый/серый)
        """
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            if item.text() == mod_name:
                if status == 'has_update':
                    item.setForeground(QColor("#00AA00"))  # Зеленый
                elif status == 'not_found':
                    item.setForeground(QColor("#CC0000"))  # Красный
                elif status == 'up_to_date':
                    item.setForeground(QColor("#AAAA00"))  # Желтый
                else:
                    item.setForeground(QColor("#888888"))  # Серый (по умолчанию)
                break
    
    def on_item_clicked(self, item):
        """Обработка клика по элементу списка"""
        # Игнорируем клик по заглушке
        if item.text() != self.PLACEHOLDER_TEXT:
            self.mod_selected.emit(item.text())
    
    def on_selection_changed(self):
        """Обработка изменения выделения"""
        selected = self.get_selected_mods()
        self.mods_selection_changed.emit(selected)
    
    def get_selected_mods(self):
        """Возвращает список выбранных модов"""
        selected = []
        for item in self.mod_list.selectedItems():
            if item.text() != self.PLACEHOLDER_TEXT:
                selected.append(item.text())
        return selected
    
    def select_all(self):
        """Выделяет все моды в списке"""
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            if item.text() != self.PLACEHOLDER_TEXT:
                item.setSelected(True)
    
    def clear_selection(self):
        """Снимает выделение со всех модов"""
        self.mod_list.clearSelection()
    
    def get_all_mods(self):
        """Возвращает список всех модов"""
        mods = []
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            if item.text() != self.PLACEHOLDER_TEXT:
                mods.append(item.text())
        return mods
    
    def clear_all_statuses(self):
        """Сбрасывает цвета всех модов в серый (не проверен)"""
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            if item.text() != self.PLACEHOLDER_TEXT:
                item.setForeground(QColor("#888888"))
