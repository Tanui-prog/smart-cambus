@echo off
echo Setting up Smart Campus Security System...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Create necessary directories
mkdir logs
mkdir media
mkdir media\incidents
mkdir media\cameras

REM Copy environment file
copy .env.example .env

REM Setup database
python manage.py makemigrations
python manage.py migrate

echo.
echo Setup complete! Next steps:
echo 1. Edit the .env file with your configuration
echo 2. Create a superuser: python manage.py createsuperuser
echo 3. Start the development server: python manage.py runserver
echo.
echo For production deployment, please refer to the README.md file.
