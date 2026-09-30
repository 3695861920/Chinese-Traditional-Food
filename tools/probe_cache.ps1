$ErrorActionPreference = 'Continue'

Write-Output '=== gradle-9.2.1-bin 目录内容 ==='
$d = Join-Path $env:USERPROFILE '.gradle\wrapper\dists\gradle-9.2.1-bin'
Get-ChildItem $d -ErrorAction SilentlyContinue | ForEach-Object {
    $kind = if ($_.PSIsContainer) { 'DIR ' } else { 'FILE' }
    Write-Output ("  $kind " + $_.Name)
    if ($_.PSIsContainer) {
        Get-ChildItem $_.FullName -ErrorAction SilentlyContinue | ForEach-Object { Write-Output ("        " + $_.Name) }
    }
}

Write-Output ''
Write-Output '=== 缓存里的 neoforge 版本 ==='
$neo = Join-Path $env:USERPROFILE '.gradle\caches\modules-2\files-2.1\net.neoforged\neoforge'
Get-ChildItem $neo -ErrorAction SilentlyContinue | ForEach-Object { Write-Output ("  " + $_.Name) }

Write-Output ''
Write-Output '=== 缓存里的 moddev-gradle 版本 ==='
$mdg = Join-Path $env:USERPROFILE '.gradle\caches\modules-2\files-2.1\net.neoforged\moddev-gradle'
Get-ChildItem $mdg -ErrorAction SilentlyContinue | ForEach-Object { Write-Output ("  " + $_.Name) }

Write-Output ''
Write-Output '=== 缓存里的 neoform 版本 ==='
$nf = Join-Path $env:USERPROFILE '.gradle\caches\modules-2\files-2.1\net.neoforged\neoform'
Get-ChildItem $nf -ErrorAction SilentlyContinue | ForEach-Object { Write-Output ("  " + $_.Name) }

Write-Output ''
Write-Output '=== 所有已缓存的 minecraft 版本 ==='
$mc = Join-Path $env:USERPROFILE '.gradle\caches\modules-2\files-2.1\com.mojang\minecraft'
Get-ChildItem $mc -ErrorAction SilentlyContinue | ForEach-Object { Write-Output ("  " + $_.Name) }

Write-Output ''
Write-Output '=== gradle user home 位置 ==='
Write-Output ("  " + $env:GRADLE_USER_HOME)
Write-Output ("  default: " + (Join-Path $env:USERPROFILE '.gradle'))
