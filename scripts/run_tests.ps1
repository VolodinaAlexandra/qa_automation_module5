param([string]$Browser = 'chromium', [string]$Channel = '')
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$env:PIP_CONFIG_FILE = Join-Path $PSScriptRoot '../config/pip.ini'
New-Item -ItemType Directory -Path 'artifacts' -Force | Out-Null
if (Test-Path -LiteralPath 'allure-results') {
    $projectRoot = (Get-Location).Path
    $previousResults = (Resolve-Path -LiteralPath 'allure-results').Path
    $archiveResults = Join-Path $projectRoot ('artifacts/allure-previous-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    if (-not $previousResults.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar)) { throw 'Unexpected results directory' }
    Move-Item -LiteralPath $previousResults -Destination $archiveResults
}
$options = @('--browser', $Browser)
$env:BROWSER_CHANNEL = $Channel
if ($Channel) { $options += @('--browser-channel', $Channel); $env:BROWSER_CHANNEL = $Channel }
python -m pytest tests/unit --cov=app --cov-branch --cov-report=html:artifacts/htmlcov --cov-report=json:artifacts/coverage.json --junitxml=artifacts/unit.xml --alluredir=allure-results
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest tests/api tests/ui @options --junitxml=artifacts/integration.xml --alluredir=allure-results
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$env:BDD_BROWSER = $Browser
python -m behave -f pretty -o - -f allure_behave.formatter:AllureFormatter -o allure-results features
exit $LASTEXITCODE
