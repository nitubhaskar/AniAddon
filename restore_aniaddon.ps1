# PowerShell script to restore Kodi environment and Git branch to AniAddon
Write-Host "Restoring to AniAddon..." -ForegroundColor Cyan

$repoPath = "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing"
$kodiAddons = "$env:APPDATA\Kodi\addons"

# 1. Switch Git branch
Set-Location $repoPath
git checkout aniaddon

# 2. Update Junctions
Remove-Item -ErrorAction SilentlyContinue "$kodiAddons\plugin.video.test"
Remove-Item -ErrorAction SilentlyContinue "$kodiAddons\context.test"

New-Item -ItemType Junction -Path "$kodiAddons\plugin.video.aniaddon" -Target "$repoPath\plugin.video.aniaddon" -Force
New-Item -ItemType Junction -Path "$kodiAddons\context.aniaddon" -Target "$repoPath\context.aniaddon" -Force

Write-Host "Successfully restored to AniAddon!" -ForegroundColor Green
