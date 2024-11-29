# =======================
# Powered By ZZBuAoYe
# 2024/11/29
# Enjoy :)
# =======================

import PyInstaller.__main__
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# Pyinstall 打包的参数
PyInstaller.__main__.run([
    'Clut-Injecort.py',  # 主程序文件
    '--name=ClutInjector',  # 输出的exe名称
    '--windowed',  # 使用GUI模式
    '--icon=icons/logo.png',  # 程序图标
    '--add-data=icons/*;icons/',  # 添加icons文件夹
    '--add-data=ClutInject_Kernel.dll;.',  # 添加DLL文件
    '--clean',  # 清理临时文件
    '--noupx',  # 不使用UPX压缩
    '--noconfirm',  # 覆盖输出目录
    '--noconsole',  # 不显示控制台
    '--onefile',  # 打包成单个文件
    '--collect-all=icons',
    '--collect-binaries=.',
]) 