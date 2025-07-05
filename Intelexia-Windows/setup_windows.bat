@echo off
echo ========================================
echo Intelexia Windows Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version

REM Create virtual environment
echo.
echo [INFO] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [INFO] Installing basic dependencies...
pip install numpy Pillow

echo [INFO] Installing OpenVINO GenAI (pre-production version for better Windows support)...
pip install --pre openvino openvino-tokenizers openvino-genai --extra-index-url https://storage.openvinotoolkit.org/simple/wheels/nightly
if errorlevel 1 (
    echo [ERROR] Failed to install OpenVINO dependencies
    echo [INFO] Trying stable versions...
    pip install openvino==2025.2 openvino-tokenizers==2025.2 openvino-genai==2025.2
)

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Download Intel NPU Driver from:
echo    https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html
echo.
echo 2. Download models using:
echo    cd Models
echo    optimum-cli export openvino -m meta-llama/Llama-3.1-8B-Instruct --weight-format int4 --sym --ratio 1.0 --group-size -1 Llama-3.1-8B-Instruct
echo    optimum-cli export openvino --model dreamlike-art/dreamlike-anime-1.0 --task stable-diffusion --weight-format fp16 dreamlike_anime_1_0_ov/FP16
echo.
echo 3. Run the application:
echo    python Intelexia-Free.py
echo.
pause
