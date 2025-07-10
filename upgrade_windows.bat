@echo off
echo POA v5 업그레이드 파일 교체 스크립트
echo =====================================
echo.

set POA_PATH=C:\Temp\POA

echo 1. 백업 폴더 생성...
if not exist "%POA_PATH%\backup" mkdir "%POA_PATH%\backup"

echo 2. 기존 파일 백업...
copy "%POA_PATH%\exchange\model\schemas.py" "%POA_PATH%\backup\schemas.py.bak" >nul 2>&1
copy "%POA_PATH%\exchange\pexchange.py" "%POA_PATH%\backup\pexchange.py.bak" >nul 2>&1
copy "%POA_PATH%\exchange\stock\kis.py" "%POA_PATH%\backup\kis.py.bak" >nul 2>&1
copy "%POA_PATH%\exchange\__init__.py" "%POA_PATH%\backup\__init__.py.bak" >nul 2>&1
copy "%POA_PATH%\requirements.txt" "%POA_PATH%\backup\requirements.txt.bak" >nul 2>&1

echo 3. 업그레이드 파일 교체...
copy /Y "%POA_PATH%\exchange\model\schemas_upgraded.py" "%POA_PATH%\exchange\model\schemas.py" >nul
copy /Y "%POA_PATH%\exchange\pexchange_upgraded.py" "%POA_PATH%\exchange\pexchange.py" >nul
copy /Y "%POA_PATH%\exchange\stock\kis_upgraded.py" "%POA_PATH%\exchange\stock\kis.py" >nul
copy /Y "%POA_PATH%\exchange\__init___upgraded.py" "%POA_PATH%\exchange\__init__.py" >nul
copy /Y "%POA_PATH%\requirements_upgraded.txt" "%POA_PATH%\requirements.txt" >nul

echo 4. 업그레이드 파일 삭제...
del "%POA_PATH%\exchange\model\schemas_upgraded.py" >nul 2>&1
del "%POA_PATH%\exchange\pexchange_upgraded.py" >nul 2>&1
del "%POA_PATH%\exchange\stock\kis_upgraded.py" >nul 2>&1
del "%POA_PATH%\exchange\__init___upgraded.py" >nul 2>&1
del "%POA_PATH%\requirements_upgraded.txt" >nul 2>&1

echo.
echo 업그레이드 완료!
echo.
echo 다음 단계:
echo 1. .env.template 파일을 .env로 복사하여 API 키 설정
echo 2. Python 가상환경 활성화 후 pip install -r requirements.txt 실행
echo.
pause
