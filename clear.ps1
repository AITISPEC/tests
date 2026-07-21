powershell -NoExit -Command ". '.venv\Scripts\Activate.ps1'; pip freeze > req.txt; pip uninstall -r req.txt -y; Remove-Item req.txt"
