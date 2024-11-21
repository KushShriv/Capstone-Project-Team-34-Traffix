@echo off
echo Starting all scripts...

:: Run each Python script in a new window
start python image_capturing.py
start python orchestrator.py

echo All scripts have been started.
