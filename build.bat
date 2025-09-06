@echo off
echo Установка зависимостей...
pip install -r requirements.txt

echo Сборка сервера (onedir)...
python server_build.py

echo Сборка клиента (onefile)...
python main_build.py

echo Сборка завершена!
pause