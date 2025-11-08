$proj = Split-Path -Parent $MyInvocation.MyCommand.Definition
$python = Join-Path $proj ".venv\Scripts\python.exe"
& $python (Join-Path $proj "training_pipeline\train_models.py")
