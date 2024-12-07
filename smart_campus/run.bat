@echo off
echo Starting Smart Campus Security System...

REM Activate virtual environment or create if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\django" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "media\incidents" mkdir media\incidents
if not exist "media\cameras" mkdir media\cameras

REM Initialize database if needed
if not exist "db.sqlite3" (
    echo Setting up database...
    python manage.py makemigrations
    python manage.py migrate
    echo.
    echo Creating superuser account...
    python manage.py createsuperuser
)

echo.
echo Starting servers...

REM Start Django development server
start cmd /k "venv\Scripts\activate && python manage.py runserver"

REM Start Daphne for WebSocket support
start cmd /k "venv\Scripts\activate && daphne -p 8001 smart_campus.asgi:application"

echo.
echo Smart Campus Security System is running!
echo.
echo Access the application at:
echo Main application: http://127.0.0.1:8000
echo Admin interface: http://127.0.0.1:8000/admin
echo.
echo Press any key to stop all servers...
pause

REM Clean up
taskkill /F /IM python.exe > nul 2>&1
