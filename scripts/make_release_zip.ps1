param(
  [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$ProjectFile = Join-Path $Root "pyproject.toml"
$VersionLine = Select-String -Path $ProjectFile -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
if (-not $VersionLine) {
  throw "Could not read version from pyproject.toml."
}

$Version = $VersionLine.Matches[0].Groups[1].Value
$PackageName = "Bantarama-v$Version"
$DistDir = Join-Path $Root $OutputDir
$StageRoot = Join-Path $DistDir "_release_staging"
$StageDir = Join-Path $StageRoot $PackageName
$ZipPath = Join-Path $DistDir "$PackageName.zip"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
$ResolvedDist = (Resolve-Path $DistDir).Path

function Assert-UnderDist([string]$PathToCheck) {
  $parent = Split-Path -Parent $PathToCheck
  if (-not (Test-Path $parent)) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
  }
  $resolved = if (Test-Path $PathToCheck) {
    (Resolve-Path $PathToCheck).Path
  } else {
    [System.IO.Path]::GetFullPath($PathToCheck)
  }
  if (-not $resolved.StartsWith($ResolvedDist, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to touch path outside dist: $resolved"
  }
}

Assert-UnderDist $StageRoot
Assert-UnderDist $ZipPath

if (Test-Path $StageRoot) {
  Remove-Item -LiteralPath $StageRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $StageDir | Out-Null

$ExcludedDirs = @(
  ".git",
  "__pycache__",
  ".pytest_cache",
  ".mypy_cache",
  ".venv",
  "venv",
  "dist",
  "build",
  "data",
  "exports",
  "htmlcov"
)
$ExcludedFiles = @(
  "*.pyc",
  "*.pyo",
  "*.log",
  ".coverage",
  "*.tmp",
  "*.zip"
)

function Test-ExcludedPath([System.IO.FileSystemInfo]$Item) {
  $rootPrefix = $Root.TrimEnd("\") + "\"
  if ($Item.FullName.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    $relative = $Item.FullName.Substring($rootPrefix.Length)
  } else {
    $relative = $Item.Name
  }
  $parts = $relative -split '[\\/]'
  foreach ($dir in $ExcludedDirs) {
    if ($parts -contains $dir) {
      return $true
    }
  }
  if (-not $Item.PSIsContainer) {
    foreach ($pattern in $ExcludedFiles) {
      if ($Item.Name -like $pattern) {
        return $true
      }
    }
  }
  return $false
}

function Copy-ReleaseItem([System.IO.FileSystemInfo]$Source, [string]$Destination) {
  if (Test-ExcludedPath $Source) {
    return
  }
  if ($Source.PSIsContainer) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Get-ChildItem -LiteralPath $Source.FullName -Force | ForEach-Object {
      Copy-ReleaseItem $_ (Join-Path $Destination $_.Name)
    }
  } else {
    Copy-Item -LiteralPath $Source.FullName -Destination $Destination -Force
  }
}

Get-ChildItem -LiteralPath $Root -Force | ForEach-Object {
  Copy-ReleaseItem $_ (Join-Path $StageDir $_.Name)
}

if (Test-Path $ZipPath) {
  Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -Path $StageDir -DestinationPath $ZipPath -CompressionLevel Optimal
Remove-Item -LiteralPath $StageRoot -Recurse -Force

Write-Host "Created release ZIP:"
Write-Host $ZipPath
