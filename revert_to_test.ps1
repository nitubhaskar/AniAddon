# PowerShell script to revert Kodi environment and Git branch back to Test
Write-Host "Reverting to Test..." -ForegroundColor Yellow

$repoPath = "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing"
$kodiAddons = "$env:APPDATA\Kodi\addons"

# 1. Switch Git branch
Set-Location $repoPath
git checkout test-addon

# 2. Update Junctions
Remove-Item -ErrorAction SilentlyContinue "$kodiAddons\plugin.video.aniaddon"
Remove-Item -ErrorAction SilentlyContinue "$kodiAddons\context.aniaddon"

New-Item -ItemType Junction -Path "$kodiAddons\plugin.video.test" -Target "$repoPath\plugin.video.test" -Force
New-Item -ItemType Junction -Path "$kodiAddons\context.test" -Target "$repoPath\context.test" -Force

Write-Host "Successfully reverted to Test!" -ForegroundColor Green
