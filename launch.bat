@echo off
REM Script de lancement - Simulation Fog Vehiculaire
REM Demarre SUMO-GUI + Dashboard temps reel

echo ============================================================
echo   Simulation Fog-Assisted Vehicular Computing
echo   SUMO + iFogSim + Dashboard
echo ============================================================

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Erreur] Python non trouve. Installez Python 3.8+
    pause
    exit /b 1
)

REM Installer dependances si necessaire
if not exist "venv" (
    echo [Setup] Creation environnement virtuel...
    python -m venv venv
)

call venv\Scripts\activate
pip install -q -r requirements.txt

REM Lancer dashboard avec SUMO
echo.
echo [Lancement] Dashboard: http://localhost:5000
echo [Lancement] SUMO-GUI se lance automatiquement
echo.
echo Appuyez Ctrl+C pour arreter
echo.

python server.py --dashboard --gui
