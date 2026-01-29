@echo off
cd /d "c:\Users\admin\Documents\Berkeley\Careers\Trellis"
echo ========================================================
echo Starting Climate Tech Bridge Rounds Visualization...
echo ========================================================
echo.
echo Please wait while the application starts.
echo It will automatically open in your default web browser.
echo.
echo DO NOT CLOSE THIS WINDOW while using the website.
echo.
python -m streamlit run app.py
pause
