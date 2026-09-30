$ErrorActionPreference = 'Continue'

Write-Output '=== gradle wrapper dists (已下载的 Gradle 发行版) ==='
$dists = Join-Path $env:USERPROFILE '.gradle\wrapper\dists'
if (Test-Path $dists) {
    Get-ChildItem $dists | ForEach-Object { Write-Output ("  " + $_.Name) }
} else {
    Write-Output '  (无)'
}

Write-Output ''
Write-Output '=== gradle caches 里的 net.neoforged ==='
$neo = Join-Path $env:USERPROFILE '.gradle\caches\modules-2\files-2.1\net.neoforged'
if (Test-Path $neo) {
    Get-ChildItem $neo | ForEach-Object { Write-Output ("  " + $_.Name) }
} else {
    Write-Output '  (无)'
}

Write-Output ''
Write-Output '=== maven.neoforged.net 连通性（curl / Schannel）==='
foreach ($mode in @('--ipv4', '--ipv6', '')) {
    $label = if ($mode) { $mode } else { 'auto' }
    $out = & curl.exe -sS -o NUL -w "%{http_code}" --max-time 20 $mode https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml 2>&1
    Write-Output ("  " + $label.PadRight(6) + " -> " + ($out -join ' '))
}

Write-Output ''
Write-Output '=== services.gradle.org 连通性 ==='
foreach ($mode in @('--ipv4', '--ipv6', '')) {
    $label = if ($mode) { $mode } else { 'auto' }
    $out = & curl.exe -sS -o NUL -w "%{http_code}" --max-time 20 $mode -L https://services.gradle.org/distributions/gradle-9.2.1-bin.zip 2>&1
    Write-Output ("  " + $label.PadRight(6) + " -> " + ($out -join ' '))
}

Write-Output ''
Write-Output '=== 本机是否有其它 NeoForge 工程（可参考其仓库配置）==='
Get-ChildItem (Join-Path $env:USERPROFILE 'Documents') -Directory -ErrorAction SilentlyContinue |
    ForEach-Object {
        if (Test-Path (Join-Path $_.FullName 'build.gradle')) { Write-Output ("  " + $_.FullName) }
    }
