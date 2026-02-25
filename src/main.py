import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSplitter, QStatusBar,
    QGroupBox, QListWidget, QListWidgetItem, QFileDialog,
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon, QFont


class ModListWidget(QListWidget):
    """Виджет для отображения списка модов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка внешнего вида"""
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.add_test_items()
        
    def add_test_items(self):
        """Добавляет тестовые элементы для предварительного просмотра"""
        test_mods = [
            "minecraft.jar (игра)",
            "jei-1.20.1.jar",
            "create-1.20.1.jar",
            "curios-1.20.1.jar",
            "patchouli-1.20.1.jar",
        ]
        
        for mod_name in test_mods:
            item = QListWidgetItem(mod_name)
            item.setFont(QFont("Consolas", 10))
            item.setData(Qt.ItemDataRole.UserRole, {
                "name": mod_name,
                "version": "1.20.1",
                "enabled": True,
                "path": str(Path("dummy/path") / mod_name)
            })
            self.addItem(item)


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.mod_folder = ""
        self.output_folder = ""
        self.settings = QSettings("ModMatcher", "ModMatcher")  # Для сохранения настроек
        self.setup_ui()
        self.setup_status_bar()
        self.load_saved_folders()  # Загружаем сохраненные папки
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        # Основные параметры окна
        self.setWindowTitle("ModMatcher - Minecraft Mod Manager")
        self.setMinimumSize(900, 600)
        self.resize(1024, 768)
        
        # Устанавливаем иконку
        self.set_window_icon()
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # === Верхняя панель с путями ===
        paths_frame = QFrame()
        paths_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        paths_frame.setMaximumHeight(150)
        
        paths_layout = QVBoxLayout(paths_frame)
        
        # Заголовок
        paths_title = QLabel("📁 Настройка папок")
        paths_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        paths_layout.addWidget(paths_title)
        
        # Папка с модами
        mod_folder_layout = QHBoxLayout()
        mod_folder_label = QLabel("Папка с модами:")
        mod_folder_label.setMinimumWidth(120)
        self.mod_folder_edit = QLineEdit()
        self.mod_folder_edit.setPlaceholderText("Выберите папку, где находятся ваши моды...")
        self.mod_folder_edit.setReadOnly(True)
        self.mod_folder_edit.setStyleSheet("""
    QLineEdit {
        background-color: #f0f0f0;
        color: #000000;  /* Черный текст */
        border: 1px solid #ccc;
        border-radius: 3px;
        padding: 3px;
    }
    QLineEdit:disabled {
        color: #333333;  /* Темно-серый для disabled состояния */
    }
""")
        
        mod_folder_btn = QPushButton("📁 Обзор...")
        mod_folder_btn.clicked.connect(self.select_mod_folder)
        mod_folder_btn.setMaximumWidth(100)
        
        mod_folder_layout.addWidget(mod_folder_label)
        mod_folder_layout.addWidget(self.mod_folder_edit)
        mod_folder_layout.addWidget(mod_folder_btn)
        paths_layout.addLayout(mod_folder_layout)
        
        # Папка для сохранения
        output_folder_layout = QHBoxLayout()
        output_folder_label = QLabel("Папка для сохранения:")
        output_folder_label.setMinimumWidth(120)
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setPlaceholderText("Выберите папку для сохранения обновленных модов...")
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setStyleSheet("""
    QLineEdit {
        background-color: #f0f0f0;
        color: #000000;
        border: 1px solid #ccc;
        border-radius: 3px;
        padding: 3px;
    }
""")
        
        output_folder_btn = QPushButton("📁 Обзор...")
        output_folder_btn.clicked.connect(self.select_output_folder)
        output_folder_btn.setMaximumWidth(100)
        
        output_folder_layout.addWidget(output_folder_label)
        output_folder_layout.addWidget(self.output_folder_edit)
        output_folder_layout.addWidget(output_folder_btn)
        paths_layout.addLayout(output_folder_layout)
        
        # Кнопка сканирования (станет активной когда выбраны обе папки)
        self.scan_button = QPushButton("🔍 Сканировать моды")
        self.scan_button.setEnabled(False)
        self.scan_button.clicked.connect(self.scan_mods)
        self.scan_button.setMaximumWidth(200)
        paths_layout.addWidget(self.scan_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(paths_frame)
        
        # === Основная рабочая область ===
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - список модов
        left_panel = QGroupBox("Список модов")
        left_layout = QVBoxLayout(left_panel)
        
        # Добавляем список модов
        self.mod_list = ModListWidget()
        left_layout.addWidget(self.mod_list)
        
        # Правая панель - информация о моде
        right_panel = QGroupBox("Информация о моде")
        right_layout = QVBoxLayout(right_panel)
        
        # Заглушка для информации
        self.info_label = QLabel("Выберите мод для просмотра информации")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: gray; padding: 20px;")
        right_layout.addWidget(self.info_label)
        
        # Добавляем панели в сплиттер
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Устанавливаем начальные размеры
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter, 1)
        
        # === Нижняя панель с кнопками ===
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        buttons_frame.setMaximumHeight(80)
        
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.addStretch()
        
        # Кнопки
        self.update_btn = QPushButton("🔄 Обновить выбранные")
        self.update_btn.setEnabled(False)
        self.update_btn.setToolTip("Будет доступно в 4-м спринте")
        buttons_layout.addWidget(self.update_btn)
        
        settings_btn = QPushButton("⚙️ Настройки")
        settings_btn.setEnabled(False)
        settings_btn.setToolTip("Будет доступно в 7-м спринте")
        buttons_layout.addWidget(settings_btn)
        
        main_layout.addWidget(buttons_frame)
        
        # Подключаем сигнал выбора элемента в списке
        self.mod_list.itemClicked.connect(self.on_mod_selected)
        
    def select_mod_folder(self):
        """Открывает диалог выбора папки с модами"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку с модами Minecraft",
            self.mod_folder or str(Path.home())
        )
        
        if folder:
            self.mod_folder = folder
            self.mod_folder_edit.setText(folder)
            self.settings.setValue("mod_folder", folder)
            self.check_scan_button_state()
            
            # Спрашиваем, хочет ли пользователь использовать ту же папку для сохранения
            if not self.output_folder:
                reply = QMessageBox.question(
                    self,
                    "Использовать ту же папку?",
                    "Использовать эту же папку для сохранения обновленных модов?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.output_folder = folder
                    self.output_folder_edit.setText(folder)
                    self.settings.setValue("output_folder", folder)
                    self.check_scan_button_state()
                    
    def select_output_folder(self):
        """Открывает диалог выбора папки для сохранения"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения обновленных модов",
            self.output_folder or str(Path.home())
        )
        
        if folder:
            self.output_folder = folder
            self.output_folder_edit.setText(folder)
            self.settings.setValue("output_folder", folder)
            self.check_scan_button_state()
            
    def check_scan_button_state(self):
        """Проверяет, можно ли активировать кнопку сканирования"""
        if self.mod_folder and self.output_folder:
            self.scan_button.setEnabled(True)
        else:
            self.scan_button.setEnabled(False)
            
    def load_saved_folders(self):
        """Загружает сохраненные папки из настроек"""
        saved_mod_folder = self.settings.value("mod_folder", "")
        saved_output_folder = self.settings.value("output_folder", "")
        
        if saved_mod_folder and Path(saved_mod_folder).exists():
            self.mod_folder = saved_mod_folder
            self.mod_folder_edit.setText(saved_mod_folder)
            
        if saved_output_folder and Path(saved_output_folder).exists():
            self.output_folder = saved_output_folder
            self.output_folder_edit.setText(saved_output_folder)
            
        self.check_scan_button_state()
        
    def scan_mods(self):
        """Сканирует папку с модами и отображает список"""
        if not self.mod_folder or not Path(self.mod_folder).exists():
            QMessageBox.warning(
                self,
                "Ошибка",
                "Указанная папка с модами не существует!"
            )
            return
            
        # Очищаем текущий список
        self.mod_list.clear()
        
        try:
            # Ищем все .jar файлы в папке с модами
            mod_files = list(Path(self.mod_folder).glob("*.jar"))
            
            if not mod_files:
                # Если нет .jar файлов, добавляем информационное сообщение
                item = QListWidgetItem("⚠️ В папке не найдено модов (.jar файлов)")
                item.setFlags(Qt.ItemFlag.NoItemFlags)  # Делаем элемент невыбираемым
                item.setForeground(Qt.GlobalColor.gray)
                self.mod_list.addItem(item)
            else:
                # Добавляем каждый мод в список
                for mod_path in mod_files:
                    item = QListWidgetItem(mod_path.name)
                    item.setFont(QFont("Consolas", 10))
                    item.setData(Qt.ItemDataRole.UserRole, {
                        "name": mod_path.name,
                        "path": str(mod_path),
                        "size": mod_path.stat().st_size,
                        "modified": mod_path.stat().st_mtime
                    })
                    self.mod_list.addItem(item)
                    
            # Обновляем статус
            self.statusBar().showMessage(f"Найдено модов: {len(mod_files)}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сканирования",
                f"Не удалось просканировать папку:\n{str(e)}"
            )
        
    def set_window_icon(self):
        """Устанавливает иконку окна из файла"""
        possible_paths = [
            Path(__file__).parent / "icon.ico",
            Path(__file__).parent / "resources" / "icon.ico",
            Path(__file__).parent.parent / "resources" / "icon.ico",
            Path(__file__).parent / "icon.png",
        ]
        
        for icon_path in possible_paths:
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                print(f"Иконка загружена: {icon_path}")
                return
                
        print("Иконка не найдена, продолжаем без иконки")
            
    def setup_status_bar(self):
        """Настройка строки состояния"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Постоянные сообщения
        status_bar.showMessage("Готов к работе")
        
        # Виджет с версией
        version_label = QLabel("v0.1.0")
        version_label.setStyleSheet("color: gray; padding-right: 5px;")
        status_bar.addPermanentWidget(version_label)
        
    def on_mod_selected(self, item):
        """Обработчик выбора мода в списке"""
        mod_data = item.data(Qt.ItemDataRole.UserRole)
        if mod_data:
            # Форматируем размер файла
            size_bytes = mod_data.get('size', 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                
            self.info_label.setText(
                f"📄 Имя: {mod_data['name']}\n\n"
                f"📁 Путь: {mod_data['path']}\n\n"
                f"📦 Размер: {size_str}\n\n"
                f"🕒 Изменен: {mod_data.get('modified', 'неизвестно')}"
            )
            self.info_label.setStyleSheet("padding: 20px; font-family: Consolas;")
            self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Активируем кнопку обновления (для будущих спринтов)
            self.update_btn.setEnabled(True)
        else:
            self.info_label.setText("Нет данных о моде")
            self.update_btn.setEnabled(False)
            
    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    
    # Устанавливаем политику масштабирования для высоких разрешений
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем цикл обработки событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
