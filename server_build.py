import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'Server.py',
    '--name=PhoneBookServer',
    '--onedir',
    '--console',
    '--add-data=phonebook.db;.',
    '--hidden-import=sqlalchemy.ext.declarative',
    '--hidden-import=sqlalchemy.orm',
    '--hidden-import=pydantic',
    '--clean',
    '--noconfirm'
])