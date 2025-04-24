@echo off
REM LLM API Key Validator - Runner Script for Windows

REM Default values
set PORT=8501
set VENV_PATH=.venv
set SKIP_VENV=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto run
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--venv" (
    set VENV_PATH=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--skip-venv" (
    set SKIP_VENV=true
    shift
    goto parse_args
)
echo Unknown option: %~1
exit /b 1

:run
REM Run the Python script with the parsed arguments
if "%SKIP_VENV%"=="true" (
    python run.py --port %PORT% --skip-venv
) else (
    python run.py --port %PORT% --venv %VENV_PATH%
)
