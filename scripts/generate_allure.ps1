$ErrorActionPreference = 'Stop'
# Preserve history from the previous real run.
if (Test-Path 'allure-report/history') {
    New-Item -ItemType Directory -Path 'allure-results/history' -Force | Out-Null
    Get-ChildItem -LiteralPath 'allure-report/history' -File |
        Copy-Item -Destination 'allure-results/history' -Force
}
allure generate allure-results --clean -o allure-report
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
allure open allure-report
