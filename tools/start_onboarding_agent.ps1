param(
    [int]$Port = 8765,
    [switch]$NoBrowser
)

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location $Root
$env:PYTHONPATH = Join-Path $Root "src"

$ArgsList = @("-m", "onboarding_app.server", "--port", "$Port")
if ($NoBrowser) {
    $ArgsList += "--no-browser"
}

python @ArgsList
