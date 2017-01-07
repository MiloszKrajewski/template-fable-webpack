@echo off
set PROJECT_HOME=%~dp0
set VIRTUAL_ENV=%PROJECT_HOME%\python_env
set NODE_MODULES=%PROJECT_HOME%\node_modules
set PATH=%PROJECT_HOME%\scripts;%VIRTUAL_ENV%\Scripts;%NODE_MODULES%\.bin;%PATH%
set PYTHONHOME=

echo ----
echo ---- ENVIRONMENT @ %PROJECT_HOME%
echo ----
