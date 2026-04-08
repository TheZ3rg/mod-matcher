from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QSplitter, QComboBox, QLabel,
                               QPushButton, QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon

from .widgets.mod_list_widget import ModListWidget
from .widgets.mod_info_widget import ModInfoWidget
from .widgets.version_info_widget import VersionInfoWidget
from .widgets.folder_selector_widget import FolderSelectorWidget

from core.mod_manager import ModManager
from core.minecraft_versions import MinecraftVersions
from core.folder_manager import FolderManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModMatcher")
        self.setMinimumSize(1000, 700)
        self.setWindowIcon(QIcon("src/resources/icons/icon.ico"))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 10)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        self.mod_list = ModListWidget()
        splitter.addWidget(self.mod_list)
        
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Выбор директорий
        self.folder_selector = FolderSelectorWidget()
        top_layout.addWidget(self.folder_selector)

        # Фильтры (версия, API, загрузчик)
        filters_widget = QWidget()
        filters_layout = QHBoxLayout(filters_widget)
        filters_layout.setContentsMargins(20, 0, 20, 0)
        
        # Версия Minecraft
        filters_layout.addWidget(QLabel("Версия:"))
        self.versions_combobox = QComboBox()
        filters_layout.addWidget(self.versions_combobox)
        filters_layout.addStretch(1)
        
        # API/Платформа
        filters_layout.addWidget(QLabel("API:"))
        self.api_combo = QComboBox()
        self.api_combo.addItems(["Modrinth", "CurseForge"])
        filters_layout.addWidget(self.api_combo)
        filters_layout.addStretch(1)
        
        # Загрузчик
        filters_layout.addWidget(QLabel("Загрузчик:"))
        self.loader_combo = QComboBox()
        self.loader_combo.addItems(["Forge", "Fabric", "Quilt", "NeoForge"])
        filters_layout.addWidget(self.loader_combo)
        
        top_layout.addWidget(filters_widget)
        
        right_panel_layout.addWidget(top_section)
        
        # Информация о текущем моде
        self.mod_info = ModInfoWidget()
        right_panel_layout.addWidget(self.mod_info)
        
        # Виджет с информацией о найденной версии
        self.version_info = VersionInfoWidget()
        right_panel_layout.addWidget(self.version_info)
        
        # Кнопка массового обновления
        self.batch_update_btn = QPushButton("🔄 Обновить выбранные")
        self.batch_update_btn.setEnabled(False)
        self.batch_update_btn.setMinimumHeight(35)
        self.batch_update_btn.clicked.connect(self.on_batch_update)
        right_panel_layout.addWidget(self.batch_update_btn)

        splitter.addWidget(right_panel)

        # Настройка размеров сплиттера
        splitter.setSizes([400, 600])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        self.mod_manager = ModManager()
        self.load_minecraft_versions()
        
        # Подключаем сигналы
        self.folder_selector.source_folder_changed.connect(self.on_source_folder_changed)
        self.folder_selector.backup_requested.connect(self.on_backup_requested)
        self.mod_list.mod_selected.connect(self.on_mod_selected)
        self.mod_list.mods_selection_changed.connect(self.on_selection_changed)
        self.version_info.update_requested.connect(self.on_update_requested)
        self.loader_combo.currentTextChanged.connect(self.on_mod_selected_refresh)
        self.versions_combobox.currentTextChanged.connect(self.on_mod_selected_refresh)
        
        # Кэш для информации об обновлениях
        self.updates_cache = {}  # {mod_filename: update_info}
        self.current_update_info = None
        self.currently_updating = False

    def on_backup_requested(self, source_folder: str, dest_folder: str):
        """Обработчик запроса на создание бэкапа"""
        FolderManager().backup_mods(self, source_folder, dest_folder)

    def load_minecraft_versions(self):
        """Загружает список версий Minecraft в комбобокс"""
        versions = MinecraftVersions().get_version_list()
        if versions:
            self.versions_combobox.addItems(versions)
    
    def on_source_folder_changed(self, folder_path: str):
        """Обработчик выбора папки с модами"""
        self.mod_list.update_mod_list(folder_path)
        self.mod_list.clear_all_statuses()  # Сбрасываем цвета
        self.updates_cache.clear()  # Очищаем кэш обновлений
        self.current_update_info = None
        self.version_info.reset()
    
    def on_mod_selected_refresh(self):
        """Обновляет информацию при смене фильтров, если выбран мод"""
        current_item = self.mod_list.mod_list.currentItem()
        if current_item and current_item.text() != self.mod_list.PLACEHOLDER_TEXT:
            self.on_mod_selected(current_item.text())
    
    def on_mod_selected(self, mod_filename: str):
        """Обработчик выбора мода из списка"""
        folder_path = self.folder_selector.source_path.text()
        
        if not folder_path:
            return
        
        # Сбрасываем виджет информации о версии
        self.version_info.reset()
        self.current_update_info = None
        
        # Получаем локальную информацию о моде
        mod_info = self.mod_manager.get_mod_info_from_file(folder_path, mod_filename)
        
        if mod_info:
            self.mod_info.update_mod_info(
                name=mod_info["name"],
                description=mod_info["description"],
                version=mod_info["version"],
                minecraft_version=mod_info["minecraft_version"],
                author=mod_info["author"]
            )
            
            # Проверяем обновления через API
            minecraft_version = self.versions_combobox.currentText()
            loader = self.loader_combo.currentText()
            
            try:
                update_info = self.mod_manager.check_for_updates(
                    mod_filename, folder_path, minecraft_version, loader
                )
                
                # Кэшируем информацию об обновлении и обновляем цвет
                if update_info and update_info.get("version_number"):
                    self.updates_cache[mod_filename] = update_info
                    self.current_update_info = update_info
                    self.version_info.show_update_info(update_info)
                    self.version_info.update_btn.setEnabled(True)
                    # Зеленый - есть обновление
                    self.mod_list.update_mod_status(mod_filename, 'has_update')
                else:
                    # Проверяем, был ли найден мод в API
                    # Если update_info вернул None, значит мод не найден
                    self.updates_cache[mod_filename] = None
                    self.version_info.show_no_updates()
                    self.version_info.update_btn.setEnabled(False)
                    self.current_update_info = None
                    # Красный - мод не найден в API
                    self.mod_list.update_mod_status(mod_filename, 'not_found')
            except Exception as e:
                print(f"Ошибка при проверке обновлений: {e}")
                self.updates_cache[mod_filename] = None
                self.version_info.show_no_updates()
                self.version_info.update_btn.setEnabled(False)
                self.current_update_info = None
                # Красный - ошибка или мод не найден
                self.mod_list.update_mod_status(mod_filename, 'not_found')
        else:
            self.mod_info.show_not_found()
            self.version_info.show_no_updates()
            self.version_info.update_btn.setEnabled(False)
            self.current_update_info = None
            # Красный - не удалось прочитать информацию из jar
            self.mod_list.update_mod_status(mod_filename, 'not_found')
        
        # Обновляем состояние кнопки массового обновления
        self.on_selection_changed(self.mod_list.get_selected_mods())
    
    def on_selection_changed(self, selected_mods):
        """Обновляет состояние кнопки массового обновления"""
        if self.currently_updating:
            self.batch_update_btn.setEnabled(False)
            return
        
        # Проверяем, есть ли обновления для выбранных модов
        has_updates = False
        for mod in selected_mods:
            if mod in self.updates_cache and self.updates_cache[mod]:
                has_updates = True
                break
        
        self.batch_update_btn.setEnabled(len(selected_mods) > 0 and has_updates)
    
    def on_update_requested(self, _):
        """Обработчик запроса на обновление одного мода"""
        if not self.current_update_info:
            return
        
        dest_folder = self.folder_selector.dest_path.text()
        if not dest_folder:
            QMessageBox.warning(self, "Ошибка", "Выберите папку для сохранения обновлений")
            return
        
        # Блокируем кнопку на время скачивания
        self.version_info.update_btn.setEnabled(False)
        self.version_info.update_btn.setText("Скачивание...")
        
        # Запускаем скачивание
        self._download_single_mod(self.current_update_info, dest_folder, self.version_info.update_btn)
    
    def on_batch_update(self):
        """Массовое обновление выбранных модов"""
        selected_mods = self.mod_list.get_selected_mods()
        
        if not selected_mods:
            return
        
        dest_folder = self.folder_selector.dest_path.text()
        if not dest_folder:
            QMessageBox.warning(self, "Ошибка", "Выберите папку для сохранения обновлений")
            return
        
        # Собираем моды, для которых есть обновления
        mods_to_update = []
        for mod in selected_mods:
            if mod in self.updates_cache and self.updates_cache[mod]:
                mods_to_update.append((mod, self.updates_cache[mod]))
        
        if not mods_to_update:
            QMessageBox.information(self, "Информация", "Нет обновлений для выбранных модов")
            return
        
        # Запускаем массовое обновление
        self._start_batch_download(mods_to_update, dest_folder)
    
    def _download_single_mod(self, update_info, dest_folder, button_to_restore=None):
        """Скачивает один мод"""
        class DownloadThread(QThread):
            finished = Signal(bool, str)
            
            def __init__(self, manager, update_info, dest_folder):
                super().__init__()
                self.manager = manager
                self.update_info = update_info
                self.dest_folder = dest_folder
            
            def run(self):
                file_path = self.manager.download_version(self.update_info, self.dest_folder)
                self.finished.emit(file_path is not None, file_path or "")
        
        self.download_thread = DownloadThread(self.mod_manager, update_info, dest_folder)
        
        progress = QProgressDialog("Скачивание мода...", "Отмена", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        
        def on_finished(success, file_path):
            progress.close()
            if success:
                QMessageBox.information(self, "Успешно", f"Мод успешно скачан:\n{file_path}")
            else:
                QMessageBox.critical(self, "Ошибка", "Ошибка при скачивании мода")
            
            if button_to_restore:
                button_to_restore.setText("Обновить")
                button_to_restore.setEnabled(True)
        
        self.download_thread.finished.connect(on_finished)
        self.download_thread.start()
    
    def _start_batch_download(self, mods_to_update, dest_folder):
        """Запускает последовательное скачивание обновлений"""
        self.currently_updating = True
        self.batch_update_btn.setEnabled(False)
        
        # Диалог прогресса
        self.batch_progress = QProgressDialog("Подготовка к скачиванию...", "Отмена", 0, len(mods_to_update), self)
        self.batch_progress.setWindowModality(Qt.WindowModal)
        self.batch_progress.setAutoClose(True)
        
        # Результаты скачивания
        self.download_results = []
        self.current_index = 0
        self.cancel_download = False
        
        def download_next():
            if self.cancel_download or self.current_index >= len(mods_to_update):
                finish_download()
                return
            
            mod_name, update_info = mods_to_update[self.current_index]
            self.batch_progress.setLabelText(f"Скачивание: {mod_name}")
            self.batch_progress.setValue(self.current_index)
            
            class SingleDownloadThread(QThread):
                finished = Signal(object)
                
                def __init__(self, manager, mod_name, update_info, dest_folder):
                    super().__init__()
                    self.manager = manager
                    self.mod_name = mod_name
                    self.update_info = update_info
                    self.dest_folder = dest_folder
                
                def run(self):
                    file_path = self.manager.download_version(self.update_info, self.dest_folder)
                    self.finished.emit((self.mod_name, file_path is not None, file_path))
            
            self.download_thread = SingleDownloadThread(
                self.mod_manager, mod_name, update_info, dest_folder
            )
            self.download_thread.finished.connect(on_download_finished)
            self.download_thread.start()
        
        def on_download_finished(result):
            mod_name, success, file_path = result
            self.download_results.append((mod_name, success, file_path))
            self.current_index += 1
            
            if self.batch_progress.wasCanceled():
                self.cancel_download = True
            
            download_next()
        
        def finish_download():
            self.currently_updating = False
            self.batch_progress.close()
            
            # Показываем результаты
            success_count = sum(1 for r in self.download_results if r[1])
            fail_count = len(self.download_results) - success_count
            
            message = f"Завершено: {success_count} успешно, {fail_count} ошибок"
            
            if fail_count > 0:
                failed_mods = [r[0] for r in self.download_results if not r[1]]
                message += f"\n\nНе удалось скачать:\n" + "\n".join(failed_mods)
            
            QMessageBox.information(self, "Результаты обновления", message)
            
            # Обновляем состояние кнопок
            self.batch_update_btn.setEnabled(True)
            self.on_selection_changed(self.mod_list.get_selected_mods())
        
        # Начинаем скачивание
        download_next()
