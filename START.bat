@echo off
git pull -allow-unrelated-histories
echo Activating virtual environment...
call venv\Scripts\activate
echo Starting the bot...
python main.py
pause
