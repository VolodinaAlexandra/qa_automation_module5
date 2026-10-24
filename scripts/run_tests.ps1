param([string]$Browser = 'chromium', [string]$Channel = '')
$ErrorActionPreference = 'Stop'
$env:PIP_CONFIG_FILE = Join-Path $PSScriptRoot '../config/pip.ini'
New-Item -ItemType Directory -Path 'artifacts' -Force | Out-Null
$options = @('--browser', $Browser)
if ($Channel) { $options += @('--browser-channel', $Channel); $env:BROWSER_CHANNEL = $Channel }
python -m pytest tests/unit --cov=app --cov-branch --cov-report=html:artifacts/htmlcov --cov-report=json:artifacts/coverage.json --junitxml=artifacts/unit.xml --alluredir=allure-results
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest tests/api tests/ui @options --junitxml=artifacts/integration.xml --alluredir=allure-results
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$env:BDD_BROWSER = $Browser
python -m behave -f pretty -o - -f allure_behave.formatter:AllureFormatter -o allure-results features
exit $LASTEXITCODE
