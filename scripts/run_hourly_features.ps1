# Run feature pipeline using venv python
$proj = Split-Path -Parent $MyInvocation.MyCommand.Definition
$python = Join-Path $proj ".venv\Scripts\python.exe"
& $python (Join-Path $proj "feature_pipeline\run_feature_pipeline.py")
