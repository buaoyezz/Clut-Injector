import os
import sys
import ctypes
from datetime import datetime
import time

import psutil
# pywin32
import win32process
import win32gui
import win32con
import win32api
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QListWidget, QFileDialog, QFormLayout, QHBoxLayout,
    QDialog, QDialogButtonBox, QProgressBar, QTextEdit, QListWidgetItem,
    QSpinBox, QLineEdit, QCheckBox, QFileIconProvider, QComboBox
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QRect, QPoint, QSize, QTimer, 
    QSettings, QFileInfo, QMetaType
)
from PyQt5.QtGui import (
    QPainter, QBrush, QColor, QRegion, QIcon, QPalette,
    QPixmap, QImage
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QListWidget, QFileDialog, QFormLayout, QHBoxLayout,
    QDialog, QDialogButtonBox, QProgressBar, QTextEdit, QListWidgetItem,
    QSpinBox, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint, QSize, QTimer, QSettings
from PyQt5.QtGui import QPainter, QBrush, QColor, QRegion, QIcon
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QPixmap, QImage 
from PIL import Image
import io
import win32ui
from win32gui import GetWindowDC
from PyQt5.QtGui import QPixmap, QImage 
from win32con import (
    GWL_EXSTYLE, WS_EX_LAYERED, LWA_ALPHA, LWA_COLORKEY,
    SRCCOPY
)
from win32com.client import GetObject
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import threading


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)  # 设置标题栏高度

        # 初始化按钮
        self.minimize_button = QPushButton('-', self)
        self.maximize_button = QPushButton('□', self)
        self.close_button = QPushButton('     ×     ', self)

        self.minimize_button.clicked.connect(self.minimize)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.close_button.clicked.connect(self.close)

        layout = QHBoxLayout()
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.setAutoFillBackground(True)

        self.is_maximized = False
        self.old_pos = None

    def minimize(self):
        self.window().showMinimized()

    def toggle_maximize_restore(self):
        if self.is_maximized:
            self.window().showNormal()
            self.is_maximized = False
            self.maximize_button.setText('□')
        else:
            self.window().showMaximized()
            self.is_maximized = True
            self.maximize_button.setText('❐')

    def close(self):
        if QMessageBox.question(self,"Tips","You Will Close The Program! \n Are You Sure?") == QMessageBox.Yes:
            self.window().close()
        else:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                # 尝试新版本的方法
                self.old_pos = event.globalPosition().toPoint()
            except AttributeError:
                # 如果失败，使用旧版本的方法
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.old_pos is not None:
            try:
                # 尝试新版本的方法
                delta = event.globalPosition().toPoint() - self.old_pos
                self.window().move(self.window().pos() + delta)
                self.old_pos = event.globalPosition().toPoint()
            except AttributeError:
                # 如果失败，使用旧版本的方法
                delta = event.globalPos() - self.old_pos
                self.window().move(self.window().pos() + delta)
                self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QDialogButtonBox
)
import psutil


class ProcessSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择进程")
        self.setModal(True)

        # 设置对话框的大小
        self.setFixedSize(600, 400)  # 设置为你希望的大小

        self.process_list = QListWidget(self)
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("搜索进程名或PID...")
        self.search_box.textChanged.connect(self.filter_processes)

        self.select_button = QPushButton('选择', self)
        self.cancel_button = QPushButton('取消', self)
        self.button_box = QDialogButtonBox(self)

        self.button_box.addButton(self.select_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.process_list)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.processes = []

        # 初始填充所有进程
        self.populate_processes([(proc.pid, proc.name()) for proc in psutil.process_iter(['pid', 'name'])])

    def populate_processes(self, processes):
        self.process_list.clear()
        self.processes = processes
        self.update_process_list()

    def update_process_list(self):
        search_text = self.search_box.text().lower()
        self.process_list.clear()
        for pid, name in self.processes:
            if search_text in str(pid) or search_text in name.lower():
                self.process_list.addItem(f"PID: {pid} - {name}")

    def filter_processes(self):
        self.update_process_list()

    def get_selected_pid(self):
        selected_item = self.process_list.currentItem()
        if selected_item:
            pid_str = selected_item.text().split()[1]
            return int(pid_str)

        return None
current_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_dir, "ClutInject_Kernel.dll")
try:
    inject_dll = ctypes.CDLL(dll_path)
    inject_dll.InjectDLL.argtypes = [ctypes.c_uint, ctypes.c_char_p]
    inject_dll.InjectDLL.restype = ctypes.c_bool
    print("ClutInject_Kernel.dll 载入成功")
except Exception as e:
    print(f"ClutInject_Kernel.dll加载失败: {e}")


def inject_dll_into_process(process_id, dll_path):
    try:
        success = inject_dll.InjectDLL(process_id, dll_path.encode('utf-8'))
        return success
    except Exception as e:
        print(f"调用 DLL 函数时发生错误: {e}")
        QMessageBox.critical(None, "错误", f"调用 DLL 函数时发生错误: {e}")
        return False

class InjectorWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, process_id, dll_files, parent_widget=None):
        super().__init__()
        self.process_id = process_id
        self.dll_files = dll_files
        self.parent_widget = parent_widget
        self.success_count = 0

    def run(self):
        success = True
        for index, dll_path in enumerate(self.dll_files):
            if not self.perform_injection(dll_path):
                success = False
                break
            self.progress.emit(int((index + 1) / len(self.dll_files) * 100))
        self.finished.emit(success)

    def perform_injection(self, dll_path):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = inject_dll_into_process(self.process_id, dll_path)
                if result:
                    self.success_count += 1
                    if self.parent_widget:
                        self.parent_widget.log_message(f"DLL {dll_path} 注入成功！", level="INFO")
                    return True
                else:
                    if self.parent_widget:
                        self.parent_widget.log_message(f"第 {attempt + 1} 次注入失败，正在重试...", level="WARNING")
                    if attempt < max_retries - 1:
                        time.sleep(3)
            except Exception as e:
                if self.parent_widget:
                    self.parent_widget.log_message(f"注入失败 错误信息: {e}", level="ERROR")
        return False

class ProcessListItem(QListWidgetItem):
    def __init__(self, pid, name, icon=None, show_pid=True):
        super().__init__()
        self.pid = pid
        self.process_name = name  # 保存原始进程名
        
        # 根据设置决定显格式
        if show_pid:
            self.setText(f"PID: {pid} - {name}")
        else:
            self.setText(name)
            
        if icon and not icon.isNull():
            self.setIcon(icon)

    def clone(self):
        show_pid = QSettings('ClutInject', 'Settings').value('show_pid', True, bool)
        new_item = ProcessListItem(self.pid, self.process_name, show_pid=show_pid)
        if self.icon():
            new_item.setIcon(self.icon())
        return new_item

class IconWorker(QThread):
    icon_ready = pyqtSignal(int, QIcon)

    def __init__(self, pid_queue):
        super().__init__()
        self.pid_queue = pid_queue
        self.running = True
        
    def get_process_icon(self, pid):
        try:
            process = psutil.Process(pid)
            try:
                exe_path = process.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None

            if not exe_path or not os.path.exists(exe_path):
                return None

            try:
                # 使用QFileInfo直接获取图标
                file_info = QFileInfo(exe_path)
                provider = QFileIconProvider()
                icon = provider.icon(file_info)
                
                if not icon.isNull():
                    return icon
                    
                # 如果QFileIconProvider失败，尝试使用系统API
                import win32gui
                import win32con
                
                # 获取小图标
                large, small = win32gui.ExtractIconEx(exe_path, 0)
                
                try:
                    if small:
                        # 获取第一个小图标的句柄
                        handle = small[0]
                        
                        # 获取图标信息
                        icon_info = win32gui.GetIconInfo(handle)
                        hbmColor = icon_info[3]  # 彩色位图句柄
                        
                        # 创建临时文件保存图标
                        temp_path = os.path.join(os.environ['TEMP'], f'icon_{pid}.png')
                        
                        # 使用GDI+保存位图
                        from PIL import ImageGrab
                        img = ImageGrab.grab((0, 0, 16, 16))  # 创建空白图像
                        img.save(temp_path)
                        
                        # 加载为QIcon
                        icon = QIcon(temp_path)
                        
                        # 清理临时文件
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                            
                        return icon if not icon.isNull() else None
                        
                finally:
                    # 清理图标句柄
                    if large:
                        for handle in large:
                            try:
                                win32gui.DestroyIcon(handle)
                            except:
                                pass
                    if small:
                        for handle in small:
                            try:
                                win32gui.DestroyIcon(handle)
                            except:
                                pass
                                
            except Exception as e:
                return None

        except Exception as e:
            return None

        return None

    def run(self):
        while self.running:
            try:
                pid = self.pid_queue.get_nowait()
                try:
                    icon = self.get_process_icon(pid)
                    if icon and not icon.isNull():
                        self.icon_ready.emit(pid, icon)
                finally:
                    self.pid_queue.task_done()
            except Empty:
                self.running = False
                break

    def stop(self):
        self.running = False
        self.wait()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('ClutInject', 'Settings')
        self.initUI()

    def initUI(self):
        self.setWindowTitle("设置")
        layout = QVBoxLayout()

        # 线程数设置
        thread_layout = QHBoxLayout()
        thread_label = QLabel("图标加载线程数:")
        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setRange(1, 16)
        self.thread_spinbox.setValue(self.settings.value('icon_threads', 8, int))
        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.thread_spinbox)
        layout.addLayout(thread_layout)

        # 进程过滤设置
        filter_layout = QHBoxLayout()
        filter_label = QLabel("进程过滤名称:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setText(self.settings.value('process_filter', 'javaw.exe,java.exe', str))
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        # 显示设置
        self.show_pid = QCheckBox("显示进程PID")
        self.show_pid.setChecked(self.settings.value('show_pid', True, bool))
        self.show_icon = QCheckBox("显示进程图标")
        self.show_icon.setChecked(self.settings.value('show_icon', True, bool))
        
        # 修改图标位置设置
        icon_pos_layout = QHBoxLayout()
        icon_pos_label = QLabel("按钮图标位置:")
        self.icon_pos_combo = QComboBox()
        self.icon_pos_combo.addItems(["左侧", "居中", "右侧"])
        current_pos = self.settings.value('icon_position', 'left', str)
        if current_pos == 'left':
            self.icon_pos_combo.setCurrentText("左侧")
        elif current_pos == 'center':
            self.icon_pos_combo.setCurrentText("居中")
        else:
            self.icon_pos_combo.setCurrentText("右侧")
        icon_pos_layout.addWidget(icon_pos_label)
        icon_pos_layout.addWidget(self.icon_pos_combo)
        
        layout.addWidget(self.show_pid)
        layout.addWidget(self.show_icon)
        layout.addLayout(icon_pos_layout)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_settings(self):
        self.settings.setValue('icon_threads', self.thread_spinbox.value())
        self.settings.setValue('process_filter', self.filter_edit.text())
        self.settings.setValue('show_pid', self.show_pid.isChecked())
        self.settings.setValue('show_icon', self.show_icon.isChecked())
        # 保存图标位置设置
        pos_map = {"左侧": "left", "居中": "center", "右侧": "right"}
        self.settings.setValue('icon_position', pos_map[self.icon_pos_combo.currentText()])
        self.accept()

class ProcessLoaderThread(QThread):
    finished = pyqtSignal(list)
    
    def run(self):
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    processes.append((proc.info['pid'], proc.info['name']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"获取进程列表失败: {e}")
        self.finished.emit(sorted(processes, key=lambda x: x[1].lower()))

class InjectorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('ClutInject', 'Settings')
        
        self._cursor_warning_shown = False
        
        self.injected_dlls = {}
        self.highlighted_windows = {}
        self.icon_workers = []
        
        self.initUI()
        
        self.update_button_styles()
        
        self.setWindowIcon(QIcon('./icons/logo.png'))
        self.log_message("程序图标加载完成", level="DEBUG")
        
        self.log_welcome()
        self.log_message("GUI初始化完成", level="INFO")

    def log_message(self, message, level="INFO"):
        """修改后的日志方法，使用 QTimer 确保在主线程中更新 UI"""
        QTimer.singleShot(0, lambda: self._safe_append_log(message, level))
    
    def _safe_append_log(self, message, level="INFO"):
        """安全的日志追加方法"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        color_map = {
            "DEBUG": "#800080",
            "INFO": "#00FF00",
            "WARNING": "#FFA500",
            "ERROR": "#FF0000",
            "WELCOME": "<span style='font-size: 20px; background: linear-gradient(to right, #0000FF, #00FF00); color: #FFFFFF; padding: 10px; border-radius: 5px; display: inline-block;'>"
        }
        
        style = color_map.get(level, "#FFFFFF")
        
        try:
            if level == "WELCOME":
                formatted_message = f"{style}{message}</span><br>"
                self.log_box.setHtml(formatted_message + self.log_box.toHtml())
            else:
                formatted_message = f"[{level}/{current_time}] {message}"
                self.log_box.append(f'<span style="color: {style};">{formatted_message}</span>')
                
            # 确保日志滚动到底部
            self.log_box.verticalScrollBar().setValue(
                self.log_box.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            # 如果出现错误且未显示过警告，则打印警
            if not self._cursor_warning_shown:
                print(f"日志记录出现错误: {e}")
                self._cursor_warning_shown = True

    def log_welcome(self):
        message = f"Clut Injector V2.0.0 Release <br>"
        self.log_message(message, level="WELCOME")

    def initUI(self):
        layout = QHBoxLayout()
        main_layout = QVBoxLayout()
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        form_layout = QFormLayout()
        self.process_label = QLabel('目标进程:', self)
        self.process_label.setStyleSheet("background: transparent;")  # 加上透明效果
        self.process_list = QListWidget(self)
        self.detect_button = QPushButton('自动检测设置的相关进程', self)
        self.detect_button.setIcon(QIcon('icons/detect.png'))
        self.detect_button.setIconSize(QSize(20, 20))  # 设置图标大小
        self.detect_button.clicked.connect(self.detect_game_process)
        self.select_process_button = QPushButton('手动选择进程', self)
        self.select_process_button.setIcon(QIcon('icons/select.png'))
        self.select_process_button.setIconSize(QSize(20, 20))
        self.select_process_button.clicked.connect(self.select_process)

        form_layout.addRow(self.process_label, self.process_list)
        form_layout.addRow(self.detect_button, self.select_process_button)

        self.dll_label = QLabel('选择DLL文件:', self)
        self.dll_label.setStyleSheet("background: transparent;")  
        self.dll_list = QListWidget(self)
        self.browse_button = QPushButton('浏览文件夹', self)
        self.browse_button.setIcon(QIcon('icons/browse.png'))
        self.browse_button.setIconSize(QSize(20, 20))
        self.browse_button.clicked.connect(self.browseDLL)

        form_layout.addRow(self.dll_label, self.dll_list)
        form_layout.addRow(self.browse_button)

        self.inject_button = QPushButton('注入DLL', self)
        self.inject_button.setIcon(QIcon('icons/inject.png'))
        self.inject_button.setIconSize(QSize(20, 20))
        self.inject_button.clicked.connect(self.injectDLL)
        self.uninject_button = QPushButton('取消注入DLL', self)
        self.uninject_button.setIcon(QIcon('icons/uninject.png'))
        self.uninject_button.setIconSize(QSize(20, 20))
        self.uninject_button.clicked.connect(self.uninjectDLL)
        self.hint_button = QPushButton('选中窗口置顶', self)
        self.hint_button.setIcon(QIcon('icons/hint.png'))
        self.hint_button.setIconSize(QSize(20, 20))
        self.hint_button.clicked.connect(self.toggle_window_highlight)
        self.about_button = QPushButton('关于', self)
        self.about_button.setIcon(QIcon('icons/about.png'))
        self.about_button.setIconSize(QSize(20, 20))
        self.about_button.clicked.connect(self.show_about_dialog)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.inject_button)
        button_layout.addWidget(self.uninject_button)
        button_layout.addWidget(self.hint_button)
        button_layout.addWidget(self.about_button)
        
        self.settings_button = QPushButton('设置', self)
        self.settings_button.setIcon(QIcon('icons/settings.png'))
        self.settings_button.setIconSize(QSize(20, 20))
        self.settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(self.settings_button)
        
        button_layout.addWidget(self.progress_bar)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        # 创建日志框
        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 100);  /* 更轻微的半透明黑色背景 */
                color: #fff;
                font-family: 'Microsoft YaHei';
                border: 1px solid #4a4a4a;
                border-radius: 15px;
                padding: 5px;
            }
        """)

        layout.addLayout(main_layout)
        layout.addWidget(self.log_box)

        self.setLayout(layout)
        self.setWindowTitle('Clut Injector B2001129 For windows X64')
        self.setGeometry(400, 400, 900, 500)

        # 设置QSS样式
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei', sans-serif;
                background-color: rgba(30, 30, 30, 150);
                color: #dcdcdc;
            }
            QLabel {
                font-size: 14px;
                padding: 5px;
                color: #dcdcdc;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                background-color: #333;
                color: #dcdcdc;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
                border-color: #888;
            }
            QListWidget {
                font-size: 12px;
                padding: 5px;
                background-color: #2e2e2e;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
            }
            QProgressBar {
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                text-align: center;
                background-color: #2e2e2e;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: #4a90d9;
                border-radius: 8px;
            }
            QScrollBar:horizontal {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                height: 15px;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                width: 15px;
                border-radius: 8px;
            }
            QScrollBar::handle:horizontal {
                background: #4a90d9;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background: #4a90d9;
                border-radius: 8px;
            }
            QScrollBar::add-line:horizontal {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                border-radius: 8px;
                height: 15px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:vertical {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                border-radius: 8px;
                width: 15px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:horizontal {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                border-radius: 8px;
                height: 15px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                border-radius: 8px;
                width: 15px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                border: 1px solid #4a4a4a;
                background: #2e2e2e;
                border-radius: 5px;
            }
        """)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.radius = 15

        # 添加统一的按钮样式
        button_style = """
            QPushButton {
                text-align: left;  /* 文本左对齐 */
                padding-left: 30px;  /* 为图标留出空间 */
                font-size: 14px;
                padding: 8px 8px 8px 30px;  /* 上右下左内边距 */
                margin: 5px;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                background-color: #333;
                color: #dcdcdc;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
                border-color: #888;
            }
        """
        
        # 应用样式到所有按钮
        for button in [self.detect_button, self.select_process_button, 
                      self.browse_button, self.inject_button, 
                      self.uninject_button, self.hint_button, 
                      self.about_button, self.settings_button]:
            button.setStyleSheet(button_style)
        
        self.log_message("按钮图标加载完成", level="DEBUG")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # 画出圆角矩形
        painter.setBrush(QBrush(QColor(30, 30, 30, 200)))
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

    def detect_game_process(self):
        # 清理之前的线程
        self.cleanup_workers()
        
        current_selection = None
        if self.process_list.currentItem():
            current_pid = self.process_list.currentItem().pid
            
        self.process_list.clear()
        try:
            process_filter = self.settings.value('process_filter', 'javaw.exe,java.exe', str)
            filter_list = [name.strip().lower() for name in process_filter.split(',')]
            
            processes = [(proc.pid, proc.name()) for proc in psutil.process_iter(['pid', 'name']) 
                        if proc.name().lower() in filter_list]
            
            show_pid = self.settings.value('show_pid', True, bool)
            show_icon = self.settings.value('show_icon', True, bool)
            
            if show_icon:
                pid_queue = Queue()
                thread_count = min(self.settings.value('icon_threads', 8, int), len(processes))
                
                for pid, _ in processes:
                    pid_queue.put(pid)
                
                for _ in range(thread_count):
                    worker = IconWorker(pid_queue)
                    worker.icon_ready.connect(self.update_process_icon)
                    self.icon_workers.append(worker)
                    worker.start()
            
            for pid, name in processes:
                item = ProcessListItem(pid, name, show_pid=show_pid)
                self.process_list.addItem(item)
                if current_selection and pid == current_pid:  # 使用pid匹配
                    self.process_list.setCurrentItem(item)
                
            if self.process_list.count() == 0:
                QMessageBox.warning(self, "提示", "没有检测到相关进程")
                self.log_message("没有检测到相关进程", level="WARNING")
                
        except Exception as e:
            self.log_message(f"检测进程失败: {e}", level="ERROR")

    def cleanup_workers(self):
        self.log_message("开始清理工作线程", level="DEBUG")
        worker_count = len(self.icon_workers)
        if hasattr(self, 'icon_workers'):
            for worker in self.icon_workers:
                worker.stop()
                worker.wait()
            self.icon_workers.clear()
        self.log_message(f"已清理 {worker_count} 个工作线程", level="INFO")

    def closeEvent(self, event):
        """窗口关闭时的处理"""
        try:
            self.cleanup_workers()  # 清理线程
            event.accept()
        except Exception as e:
            self.log_message(f"关闭窗口时出错: {e}", level="ERROR")
            event.accept()

    def update_process_icon(self, pid, icon):
        try:
            for i in range(self.process_list.count()):
                item = self.process_list.item(i)
                # 通过pid匹配，而不是文本匹配
                if item.pid == pid and self.settings.value('show_icon', True, bool):
                    item.setIcon(icon)
                    break
        except Exception as e:
            self.log_message(f"更新进程图标失败: {e}", level="ERROR")

    def browseDLL(self):
        self.log_message("开始浏览DLL文件", level="DEBUG")
        options = QFileDialog.Options()
        dll_files, _ = QFileDialog.getOpenFileNames(self, "选择DLL文件", "", "DLL Files (*.dll)", options=options)
        if dll_files:
            self.dll_list.clear()
            self.dll_list.addItems(dll_files)
            self.log_message(f"已选择 {len(dll_files)} 个DLL文件", level="INFO")
            for dll in dll_files:
                self.log_message(f"DLL文件路径: {dll}", level="DEBUG")
        else:
            self.log_message("未选择任何DLL文件", level="WARNING")
    def injectDLL(self):
        self.log_message("开始DLL注入流程", level="DEBUG")
        selected_item = self.process_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "错误", "请先选择一个游戏进程")
            self.log_message("注入失败: 未选择目标进程", level="ERROR")
            return

        process_info = selected_item.text()
        process_id = int(process_info.split()[1])  # 从显示的PID中提取出进程ID

        dll_files = [self.dll_list.item(i).text() for i in range(self.dll_list.count())]
        if not dll_files:
            QMessageBox.warning(self, "错误", "请先选择要注入的DLL文件")
            self.log_message("请先选择要注入的DLL文件", level="WARNING")
            return

        reply = QMessageBox.question(
            self,
            "确认注入",
            f"即将向进程 {process_id} 注入 {len(dll_files)} 个DLL文件\n是否继续？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # 保存已注入的DLL信息
        if process_id not in self.injected_dlls:
            self.injected_dlls[process_id] = []
        self.injected_dlls[process_id].extend(dll_files)
        
        self.progress_bar.setValue(0)
        self.worker = InjectorWorker(process_id, dll_files, self)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_injection_finished)
        self.worker.start()
        
        # 禁用注入按钮，防止重复操作
        self.inject_button.setEnabled(False)


    def show_about_dialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About | 关于")
        about_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("Clut Inject")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 版本
        version_label = QLabel("Version 2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        
        # 作者
        author_label = QLabel("By: ZZBuAoYe")
        author_label.setAlignment(Qt.AlignCenter)
        
        # 描述
        desc_label = QLabel(
            "Powered by the powerful combination of\n"
            "Python and C++\n\n"
            "Kernel development by C++\n"
            "Main program development by Python"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        # 添加组件到布局
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(author_label)
        layout.addSpacing(20)  # 添加间距
        layout.addWidget(desc_label)
        layout.addStretch()  # 添加弹性空间
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(about_dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        
        about_dialog.setLayout(layout)
        
        # 设置样式
        style = """
        QDialog {
            background-color: #2b2b2b;
        }
        QLabel {
            color: #ffffff;
            font-family: 'Microsoft YaHei', Arial;
            margin: 5px;
            background-color: transparent;
        }
        QLabel:first-child {  /* 标题 */
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
            margin-top: 20px;
            background-color: transparent;
        }
        QLabel:nth-child(2) {  /* 版本 */
            font-size: 14px;
            color: #888888;
            background-color: transparent;
        }
        QLabel:nth-child(3) {  /* 作者 */
            font-size: 14px;
            color: #888888;
            background-color: transparent;
        }
        QLabel:nth-child(4) {  /* 描述 */
            font-size: 13px;
            line-height: 1.5;
            padding: 10px;
            background-color: transparent;
        }
        QPushButton {
            background-color: transparent;
            color: #ffffff;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 5px 20px;
            font-size: 13px;
            margin: 10px;
        }
        QPushButton:hover {
            background-color: rgba(68, 68, 68, 0.5);
            border: 1px solid #666666;
        }
        QPushButton:pressed {
            background-color: rgba(102, 102, 102, 0.5);
        }
        """
        
        about_dialog.setStyleSheet(style)
        
        # 设置窗口标志
        about_dialog.setWindowFlags(
            Qt.Dialog | 
            Qt.CustomizeWindowHint | 
            Qt.WindowTitleHint | 
            Qt.WindowCloseButtonHint
        )
        
        about_dialog.exec_()

    def on_injection_finished(self, success):
        # 重新启用注入按钮
        self.inject_button.setEnabled(True)
        
        if success:
            QMessageBox.information(
                self, 
                "注入成功", 
                f"成功注入 {self.worker.success_count} 个DLL文件"
            )
            self.log_message(f"成功注入 {self.worker.success_count} 个DLL文件", level="INFO")
        else:
            QMessageBox.critical(
                self, 
                "注入失败", 
                "部分或全部DLL注入失败，请查看日志了解详情"
            )
            self.log_message("DLL注入失败！", level="ERROR")

    def uninjectDLL(self):
        selected_item = self.process_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "错误", "请先选择一个游戏进程")
            self.log_message("请先选择一个游戏进程", level="ERROR")
            return

        process_info = selected_item.text()
        process_id = int(process_info.split()[1])  # 从显示的PID中提取出进程ID

        if process_id not in self.injected_dlls or not self.injected_dlls[process_id]:
            QMessageBox.warning(self, "错误", "没有DLL可取消注入")
            self.log_message("没有DLL可取消注入", level="ERROR")
            return

        # 获取进程句柄
        try:
            h_process = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process_id)
            if not h_process:
                QMessageBox.critical(self, "错误", "法打开进程")
                self.log_message("无法打开进程", level="ERROR")
                return

            # 获取所有加载的模块
            h_modules = (ctypes.c_void_p * 1024)()
            needed = ctypes.c_ulong()
            ctypes.windll.psapi.EnumProcessModules(h_process, ctypes.byref(h_modules), ctypes.sizeof(h_modules),
                                                   ctypes.byref(needed))
            num_modules = needed.value // ctypes.sizeof(ctypes.c_void_p)

            success = True
            for dll_path in self.injected_dlls[process_id]:
                h_module = None

                # 找到与dll_path匹配的模块
                for i in range(num_modules):
                    module_name = ctypes.create_string_buffer(255)
                    ctypes.windll.psapi.GetModuleFileNameExA(h_process, h_modules[i], module_name, 255)
                    if module_name.value.decode('utf-8') == dll_path:
                        h_module = h_modules[i]
                        break

                if h_module:
                    # 卸载DLL
                    h_thread = ctypes.windll.kernel32.CreateRemoteThread(h_process, None, 0,
                                                                         ctypes.windll.kernel32.FreeLibrary, h_module,
                                                                         0, None)
                    ctypes.windll.kernel32.WaitForSingleObject(h_thread, -1)
                    ctypes.windll.kernel32.CloseHandle(h_thread)
                    self.injected_dlls[process_id].remove(dll_path)
                else:
                    success = False
                    break

            ctypes.windll.kernel32.CloseHandle(h_process)

            if success:
                QMessageBox.information(self, "成功", "DLL取消注入成功")
                self.log_message("取消注入成功",level="INFO")
            else:
                QMessageBox.critical(self, "失败", "某些DLL取消注入失败")
                self.log_message("取消注入失败",level="ERROR")

        except Exception as e:
            print(f"取消注入失败 错误信息: {e}")
            QMessageBox.critical(self, "错误", f"取消注入失败 错误: {e}")
            self.log_message("取消注入失败",level="ERROR")

    def toggle_window_highlight(self):
        selected_item = self.process_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "错误", "请先选择一个游戏进程")
            self.log_message("请先选择一个游戏进程", level="ERROR")
            return

        try:
            process_id = int(selected_item.text().split()[1])
            hwnds = []

            def enum_window_callback(hwnd, _):
                _, window_process_id = win32process.GetWindowThreadProcessId(hwnd)
                if window_process_id == process_id and win32gui.IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
                return True

            win32gui.EnumWindows(enum_window_callback, None)

            if hwnds:
                for hwnd in hwnds:
                    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd):
                        try:
                            # 将窗口置顶
                            win32gui.SetWindowPos(
                                hwnd,
                                win32con.HWND_TOPMOST,
                                0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                            )
                            self.log_message("窗口已置顶", level="INFO")
                            QMessageBox.information(self, "提示", "窗口已置顶")
                        except Exception as e:
                            print(f"窗口置顶失败: {e}")
                            QMessageBox.critical(self, "错误", f"窗口置顶失败: {e}")
            else:
                QMessageBox.warning(self, "错误", "未到与该进程相关的窗口")

        except Exception as e:
            print(f"处理进程时出错: {e}")
            QMessageBox.critical(self, "错误", f"无法处理该进程: {e}")

    def choose_highlight_color(self):
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.highlight_color, self, '选择高亮颜色')
        if color.isValid():
            self.highlight_color = color
            self.log_message(f"高亮颜色已更改为: RGB({color.red()}, {color.green()}, {color.blue()})", level="INFO")

    def select_process(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("选择进程")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        
        # 搜索框
        search_box = QLineEdit()
        search_box.setPlaceholderText("搜索进程...")
        
        # 进程列表
        process_list = QListWidget()
        loading_label = QLabel("正在加载进程列表...")
        
        layout.addWidget(loading_label)
        layout.addWidget(search_box)
        layout.addWidget(process_list)
        process_list.hide()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        
        def on_process_list_loaded(processes):
            if self.settings.value('show_icon', True, bool):
                pid_queue = Queue()
                for pid, _ in processes:
                    pid_queue.put(pid)
                
                thread_count = min(self.settings.value('icon_threads', 8, int), len(processes))
                
                for _ in range(thread_count):
                    worker = IconWorker(pid_queue)
                    worker.icon_ready.connect(lambda pid, icon: update_process_icon(pid, icon))
                    self.icon_workers.append(worker)
                    worker.start()
            
            show_pid = self.settings.value('show_pid', True, bool)
            for pid, name in processes:
                item = ProcessListItem(pid, name, show_pid=show_pid)
                process_list.addItem(item)
            
            loading_label.hide()
            process_list.show()
            
            def filter_processes():
                search_text = search_box.text().lower()
                for i in range(process_list.count()):
                    item = process_list.item(i)
                    search_target = f"{item.pid} {item.process_name}".lower()
                    item.setHidden(search_text not in search_target)
            
            search_box.textChanged.connect(filter_processes)
            
        def update_process_icon(pid, icon):
            for i in range(process_list.count()):
                item = process_list.item(i)
                if item.pid == pid:
                    item.setIcon(icon)
                    break
        
        # 创建并启动进程加载线程
        loader_thread = ProcessLoaderThread()
        loader_thread.finished.connect(on_process_list_loaded)
        loader_thread.start()
        
        if dialog.exec_() == QDialog.Accepted:
            selected_item = process_list.currentItem()
            if selected_item:
                self.process_list.clear()
                self.process_list.addItem(selected_item.clone())
                self.log_message(f"已选择进程: {selected_item.text()}", level="INFO")
            else:
                self.log_message("未选择任何进程", level="WARNING")
        
        # 清理线程
        self.cleanup_workers()

    def show_settings(self):
        self.log_message("打开设置对话框", level="DEBUG")
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.log_message("设置已更新:", level="INFO")
            self.log_message(f"图标加载线程数: {self.settings.value('icon_threads')}", level="DEBUG")
            self.log_message(f"进程过滤器: {self.settings.value('process_filter')}", level="DEBUG")
            self.log_message(f"显示PID: {self.settings.value('show_pid')}", level="DEBUG")
            self.log_message(f"显示图标: {self.settings.value('show_icon')}", level="DEBUG")
            self.log_message(f"图标位置: {self.settings.value('icon_position')}", level="DEBUG")
            # 更新按钮样式
            self.update_button_styles()

    def update_button_styles(self):
        icon_position = self.settings.value('icon_position', 'left', str)
        
        # 基础按钮样式
        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                background-color: #333;
                color: #dcdcdc;
            }
        """
        
        # 根据图标位置设置不同的样式
        if icon_position == 'left':
            button_style += """
                QPushButton {
                    padding-left: 30px;
                    text-align: left;
                }
            """
        elif icon_position == 'center':
            button_style += """
                QPushButton {
                    padding-left: 15px;
                    padding-right: 15px;
                    text-align: center;
                }
            """
        else:  # right
            button_style += """
                QPushButton {
                    padding-right: 30px;
                    text-align: right;
                }
            """
            
        button_style += """
            QPushButton:hover {
                background-color: #555;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
                border-color: #888;
            }
        """
        
        # 更新所有按钮的样式和图标位置
        buttons = [
            self.detect_button, 
            self.select_process_button,
            self.browse_button, 
            self.inject_button,
            self.uninject_button, 
            self.hint_button,
            self.about_button, 
            self.settings_button
        ]
        
        for button in buttons:
            button.setStyleSheet(button_style)
            
            # 设置图标位置
            if icon_position == 'left':
                button.setLayoutDirection(Qt.LeftToRight)
            elif icon_position == 'center':
                button.setLayoutDirection(Qt.LeftToRight)  # 居中时使用左对齐
            else:
                button.setLayoutDirection(Qt.RightToLeft)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    injector = InjectorGUI()
    injector.show()
    sys.exit(app.exec_())
