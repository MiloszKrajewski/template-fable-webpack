@echo off

pushd %~dp0
setlocal

call __activate__.cmd

if not exist python_env\Scripts\python.exe (
    call py -3 -m virtualenv python_env
)

python -m pip install -U pip setuptools wheel
python -m pip install -U requests watchdog psutil

python scripts\mkshim.py scripts\mkshim.cmd scripts\mkshim.py
call mkshim scripts\download.cmd scripts\download.py

call mkshim scripts\watch.cmd scripts\watch.py
call mkshim scripts\mkfsproj.cmd scripts\mkfsproj.py

call yarn
python -m pip install -r pip.lock

endlocal
popd
