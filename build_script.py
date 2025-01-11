# =======================
# Clut Injector Build Script | Stable Release 2025/01/11
# Powered By ZZBuAoYe
# 2025/01/11
# Version: 2.0.0
# Enjoy :)
# PyInstaller: Latest Version
# =======================

# pls intall pyinstaller first // pip install pyinstaller
import PyInstaller.__main__
import os
# Select Directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Pyinstall 打包的参数
PyInstaller.__main__.run([
    'Clut-Injector.py',  # 主程序文件 | fix write name 
    '--name=ClutInjector',  # 输出的exe名称
    '--windowed',  # 使用GUI模式 | Not Show Window
    '--icon=icons/logo.png',  # 程序图标 | icons of software
    '--add-data=icons/*;icons/',  # 添加icons文件 | add icons folder
    '--add-data=ClutInject_Kernel.dll;.',  # 添加DLL文件 | add DLL file
    '--clean',  # 清理临时文件 | clean temp file
    '--noupx',  # 不使用UPX压缩 | Not use UPX compress
    '--noconfirm',  # 覆盖输出目录 | overwrite output directory
    '--noconsole',  # 不显示控制台 | Not Show Console
    '--onefile',  # 打包成单个文件 | pack into one file
    '--collect-all=icons',  # 收集所有icons文件 | collect all icons file
    '--collect-binaries=.',  # 收集所有二进制文件 | collect all binary file
]) 