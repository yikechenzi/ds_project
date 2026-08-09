"""
打包脚本 - 将应用打包为单文件 exe
运行方式: python build_exe.py
"""

import os
import sys

# PyInstaller 参数
# --noconsole: 不显示控制台窗口
# --onefile: 打包为单文件
# --windowed: 无控制台模式 (Windows)

def build():
    cmd = (
        'pyinstaller '
        '--noconsole '
        '--onefile '
        '--windowed '
        '--name "电商选品管理系统" '
        '--add-data "ui;ui" '
        '--hidden-import PySide6.QtCore '
        '--hidden-import PySide6.QtGui '
        '--hidden-import PySide6.QtWidgets '
        'main.py'
    )
    print(f"开始打包...\n命令: {cmd}\n")
    os.system(cmd)
    print("\n打包完成! exe 文件在 dist 目录中。")
    print("请将 dist/电商选品管理系统.exe 分享给用户。")

if __name__ == "__main__":
    build()
