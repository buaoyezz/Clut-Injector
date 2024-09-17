import os
import sys
import ctypes
from datetime import datetime
import time

import psutil
import win32process
import win32gui
import win32con
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QListWidget, QFileDialog, QFormLayout, QHBoxLayout,
    QDialog, QDialogButtonBox, QProgressBar, QTextEdit, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint, QSize, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor, QRegion, QIcon
from PyQt5.QtGui import QPalette, QColor


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
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.is_maximized:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.window().move(self.window().pos() + delta)
            self.old_pos = event.globalPos()

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
dll_path = os.path.join(current_dir, "NaklyInject_Kernel.dll")
try:
    inject_dll = ctypes.CDLL(dll_path)
    inject_dll.InjectDLL.argtypes = [ctypes.c_uint, ctypes.c_char_p]
    inject_dll.InjectDLL.restype = ctypes.c_bool
    print("NaklyInject_Kernel.dll 载入成功")
except Exception as e:
    print(f"NaklyInject_Kernel.dll加载失败: {e}")


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
        self.parent_widget = parent_widget  # 保存父窗口参数

    def run(self):
        success = True
        for index, dll_path in enumerate(self.dll_files):
            if not self.perform_injection(dll_path):
                success = False
                break
            self.progress.emit(int((index + 1) / len(self.dll_files) * 100))
        self.finished.emit(success)

    def perform_injection(self, dll_path):
        max_retries = 2
        for attempt in range(max_retries):
            try:
                result = inject_dll_into_process(self.process_id, dll_path)
                if result:
                    if self.parent_widget:
                        QMessageBox.information(self.parent_widget, "注入成功", "DLL 注入成功！", QMessageBox.Ok)
                    return True
                else:
                    if self.parent_widget:
                        QMessageBox.warning(self.parent_widget, "注入失败", f"第 {attempt + 1} 次注入失败", QMessageBox.Ok)
                    if attempt < max_retries - 1:
                        time.sleep(2)
            except Exception as e:
                if self.parent_widget:
                    QMessageBox.critical(self.parent_widget, "注入失败", f"注入失败 错误信息: {e}", QMessageBox.Ok)
        return False

class InjectorGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.injected_dlls = {}
        self.initUI()
        self.is_admin()
        self.log_welcome()

    def initUI(self):
        layout = QHBoxLayout()

        main_layout = QVBoxLayout()
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        form_layout = QFormLayout()
        self.process_label = QLabel('目标进程:', self)
        self.process_list = QListWidget(self)
        self.detect_button = QPushButton('自动检测Java相关进程', self)
        self.detect_button.clicked.connect(self.detect_game_process)
        self.select_process_button = QPushButton('手动选择进程', self)
        self.select_process_button.clicked.connect(self.select_process)

        form_layout.addRow(self.process_label, self.process_list)
        form_layout.addRow(self.detect_button, self.select_process_button)

        self.dll_label = QLabel('选择DLL文件:', self)
        self.dll_list = QListWidget(self)
        self.browse_button = QPushButton('浏览文件夹', self)
        self.browse_button.clicked.connect(self.browseDLL)

        form_layout.addRow(self.dll_label, self.dll_list)
        form_layout.addRow(self.browse_button)

        self.inject_button = QPushButton('注入DLL', self)
        self.inject_button.clicked.connect(self.injectDLL)
        self.uninject_button = QPushButton('取消注入DLL', self)
        self.uninject_button.clicked.connect(self.uninjectDLL)
        self.hint_button = QPushButton('窗口置顶提示', self)
        self.hint_button.clicked.connect(self.set_window_on_top)
        self.about_button = QPushButton('关于', self)
        self.about_button.clicked.connect(self.show_about_dialog)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.inject_button)
        button_layout.addWidget(self.uninject_button)
        button_layout.addWidget(self.hint_button)
        button_layout.addWidget(self.about_button)
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
        self.setWindowTitle('Nakly Inject')
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # 画出圆角矩形
        painter.setBrush(QBrush(QColor(30, 30, 30, 200)))
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

    def log_message(self, message, level="INFO"):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 颜色映射和样式设置
        color_map = {
            "DEBUG": "#800080",  # 紫
            "INFO": "#00FF00",  # 绿
            "WARNING": "#FFA500",  # 橙
            "ERROR": "#FF0000",  # 红
            "WELCOME": "<span style='font-size: 20px; background: linear-gradient(to right, #0000FF, #00FF00); color: #FFFFFF; padding: 10px; border-radius: 5px; display: inline-block;'>"
        }

        style = color_map.get(level, "#FFFFFF")  # 默认颜色为白色

        try:
            if level == "WELCOME":
                formatted_message = f"{style}{message}</span><br>"
                self.log_box.setHtml(formatted_message + self.log_box.toHtml())
            else:
                formatted_message = f"[{level}/{current_time}] {message}"
                self.log_box.append(f'<span style="color: {style};">{formatted_message}</span>')
        except Exception as e:
            print(f"记录日志时发生错误: {e}")


    def log_welcome(self):
        message = f"Nakly Inject V1.0.0 Release <br>"
        self.log_message(message, level="WELCOME")

    def detect_game_process(self):
        self.process_list.clear()
        processes = [(proc.pid, proc.name()) for proc in psutil.process_iter(['pid', 'name']) if
                     proc.name().lower() in ['javaw.exe', 'java.exe']]
        self.process_list.addItems([f"PID: {pid} - {name}" for pid, name in processes])
        if self.process_list.count() == 0:
            QMessageBox.warning(self, "提示", "没有检测到游戏进程")
            self.log_message("没有检测到游戏进程", level="WARNING")

    def browseDLL(self):
        options = QFileDialog.Options()
        dll_files, _ = QFileDialog.getOpenFileNames(self, "选择DLL文件", "", "DLL Files (*.dll)", options=options)
        if dll_files:
            self.dll_list.clear()
            self.dll_list.addItems(dll_files)
            self.log_message(f"DLL文件导入成功{dll_files}", level="INFO")
        else:
            self.log_message("未选择DLL文件", level="WARNING")
    def injectDLL(self):
        selected_item = self.process_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "错误", "请先选择一个游戏进程")
            self.log_message("请先选择一个游戏进程", level="ERROR")
            return

        process_info = selected_item.text()
        process_id = int(process_info.split()[1])  # 从显示的PID中提取出进程ID

        dll_files = [self.dll_list.item(i).text() for i in range(self.dll_list.count())]
        if not dll_files:
            QMessageBox.warning(self, "错误", "请先选择要注入的DLL文件")
            self.log_message("请先选择要注入的DLL文件", level="WARNING")
            return

        if not ctypes.windll.shell32.IsUserAnAdmin():
            reply = QMessageBox.question(
                self,
                "Tips",
                "为了提升成功概率我们推荐管理员运行本程序\n若注入失败，可以在尝试管理员运行\n[是] -自动管理员重启/并且尝试继续注入 [否] -不重启直接继续注入",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.log_message(f"收到{reply}，开始尝试重启为管理员权限,即将执行", level="INFO")
                QTimer.singleShot(3000, self.restart_as_admin)
                self.log_message("准备重启中，请稍等...", level="INFO")
            else:
                self.log_message(f"收到{reply}, 注入任务继续执行", level="INFO")
        else:
            self.log_message("环境检测完毕, 开始执行任务", level="INFO")


        self.progress_bar.setValue(0)
        self.worker = InjectorWorker(process_id, dll_files)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_injection_finished)
        self.worker.start()

    def restart_as_admin(self):
        try:
            script = os.path.abspath(sys.argv[0])

            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                f'"{script}" {" ".join(sys.argv[1:])}',
                None,
                1
            )
            QApplication.quit()
        except Exception as e:
            self.log_message(f"重启程序为管理员权限时发生异常: {e}", level="ERROR")

    def show_about_dialog(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About | 关于")
        msg_box.setText("Nakly Inject VER 1.0.0\nVersion: 1.0.0\nBy: ZZBuAoYe\nNakly Inject For Minecraft")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setFixedSize(500, 200)
        msg_box.exec_()

    def on_injection_finished(self, success):
        if success:
            QMessageBox.information(self, "Succeed", "DLL注入成功!")
            self.log_message("所有DLL注入成功", level="INFO")
        else:
            QMessageBox.critical(self, "失败", "DLL注入失败！！")
            self.log_message("DLL注入失败！", level="ERROR")
    def is_admin(self):
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                pass
            else:
                self.log_message("检测到当前环境非管理员，可能存在无法完整读取软件列表等情况[建议]在管理员权限下启动")  # 不是管理员时记录信息
        except Exception as e:
            self.log_message(f"检查管理员权限时发生异常: {e}")

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
                QMessageBox.critical(self, "错误", "无法打开进程")
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

    def set_window_on_top(self):
        selected_item = self.process_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "错误", "请先选择一个游戏进程")
            self.log_message("请先选择一个游戏进程",level="ERROR")
            return

        try:
            process_id = int(selected_item.text().split()[1])
            hwnds = []

            # 获取与目标PID相关的窗口句柄
            def enum_window_callback(hwnd, _):
                _, window_process_id = win32process.GetWindowThreadProcessId(hwnd)
                if window_process_id == process_id and win32gui.IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
                return True

            # 枚举所有窗口句柄，找到与该进程ID匹配的窗口
            win32gui.EnumWindows(enum_window_callback, None)

            if hwnds:
                for hwnd in hwnds:
                    # 检查窗口句柄是否有效，并捕获异常
                    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd):
                        try:
                            # 置顶窗口
                            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                            QMessageBox.information(self, "提示", "窗口已置顶")
                        except Exception as e:
                            print(f"设置窗口置顶失败 错误信息: {e}")
                            QMessageBox.critical(self, "错误", f"窗口置顶失败 错误: {e}")
            else:
                QMessageBox.warning(self, "错误", "未找到与该进程相关的窗口")

        except Exception as e:
            print(f"处理进程时出错 错误信息: {e}")
            QMessageBox.critical(self, "错误", f"无法处理该进程 错误: {e}")

    def select_process(self):
        all_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                all_processes.append((proc.info['pid'], proc.info['name']))  # 只保留 pid 和 name
            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                self.log_message(f"无法访问进程：{str(e)}", level="WARNING")
                continue

        self.log_message(f"获取到 {len(all_processes)} 个进程", level="INFO")

        dialog = ProcessSelectionDialog(self)
        dialog.populate_processes(all_processes)

        if dialog.exec_() == QDialog.Accepted:
            selected_pid = dialog.get_selected_pid()
            if selected_pid:
                selected_process = next((p_name for pid, p_name in all_processes if pid == selected_pid), "未知进程")
                self.log_message(f"选择成功，PID: {selected_pid} - {selected_process}，共计选择 1 个进程", level="INFO")
                self.process_list.clear()
                self.process_list.addItem(f"PID: {selected_pid} - {selected_process} 共计选择 1 个进程")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    injector = InjectorGUI()
    injector.show()
    sys.exit(app.exec_())
