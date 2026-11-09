@echo off
echo ================================================
echo Exercise Posture Analysis API Server
echo ================================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo ================================================
echo Starting server...
echo The API will be available at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo To test the API, open test_upload.html in your browser
echo ================================================
echo.
python main.py
