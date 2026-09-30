# 抓取 NeoForge MDK 的 Gradle 脚手架（只取构建文件，不覆盖我们自己的 src）。
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools/setup_build_env.ps1
#
# 说明：本仓库原本只有 src/ + tools/ + docs/，没有 Gradle 工程，
#       既不能编译验证、也不能启动客户端。这个脚本从官方 MDK 仓库
#       （MDK-26.1.2-ModDevGradle）取回构建脚手架，好让 gradlew 能跑。

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path -Parent $PSScriptRoot
$downloads = Join-Path $PSScriptRoot 'downloads'
$zipPath = Join-Path $downloads 'mdk.zip'
New-Item -ItemType Directory -Force -Path $downloads | Out-Null

$url = 'https://codeload.github.com/NeoForgeMDKs/MDK-26.1.2-ModDevGradle/zip/refs/heads/main'
Write-Output "downloading $url"
& curl.exe -sSL --max-time 120 -o $zipPath $url
if (-not (Test-Path $zipPath)) { throw 'download failed' }
Write-Output ("  -> " + (Get-Item $zipPath).Length + " bytes")

# 只取这些：构建脚本 + wrapper（wrapper 里有二进制 jar，必须原样取出）
$wanted = @(
    'build.gradle',
    'settings.gradle',
    'gradle.properties',
    'gradlew',
    'gradlew.bat',
    'gradle/wrapper/gradle-wrapper.jar',
    'gradle/wrapper/gradle-wrapper.properties'
)

$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
$prefix = $null
$extracted = @()
try {
    foreach ($entry in $zip.Entries) {
        if (-not $entry.Name) { continue }
        if (-not $prefix) {
            # 压缩包内第一层是 <repo>-main/
            $prefix = ($entry.FullName -split '/')[0] + '/'
        }
        $rel = $entry.FullName.Substring($prefix.Length)
        $rel = $rel -replace '\\', '/'
        if ($wanted -notcontains $rel) { continue }

        $target = Join-Path $root $rel
        $dir = Split-Path -Parent $target
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $target, $true)
        $extracted += $rel
        Write-Output ("  extracted " + $rel)
    }
} finally {
    $zip.Dispose()
}

Write-Output ''
Write-Output '--- result ---'
foreach ($rel in $wanted) {
    $target = Join-Path $root $rel
    if (Test-Path $target) {
        Write-Output ("OK   " + $rel + "  (" + (Get-Item $target).Length + " bytes)")
    } else {
        Write-Output ("MISS " + $rel)
    }
}
