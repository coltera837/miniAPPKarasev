@echo off
echo Сборка сервера...
pyinstaller --name=PhoneBookServer --onedir --console --hidden-import=sqlalchemy.ext.declarative --hidden-import=sqlalchemy.orm --hidden-import=pydantic --clean --noconfirm src/Server.py

echo Сборка клиента...
pyinstaller --name=PhoneBookClient --onefile --windowed --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtCore --hidden-import=requests --clean --noconfirm src/main.py

pause