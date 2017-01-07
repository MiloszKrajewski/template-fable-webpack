@echo off
pushd %~dp0
rmdir /q /s node_modules
rmdir /q /s python_env
rmdir /q /s build
popd