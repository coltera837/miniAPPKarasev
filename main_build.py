import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--name=PhoneBookClient',
    '--onefile',
    '--windowed',
    '--hidden-import=PySide6.QtWidgets',
    '--hidden-import=PySide6.QtGui',
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=requests',
    '--clean',
    '--noconfirm'
])