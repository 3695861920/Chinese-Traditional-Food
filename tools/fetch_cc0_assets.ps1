# 下载《国风·传统食物》所用的免费纹理素材（全部为 CC0 / 公有领域）。
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools/fetch_cc0_assets.ps1
#
# 素材来源与许可证：
#   1) Kenney.nl    - Pixel Platformer Food Expansion  (CC0 1.0) 18x18 像素食物
#   2) Kenney.nl    - Pixel Platformer Farm Expansion  (CC0 1.0) 18x18 像素农作物
#   3) OpenGameArt  - "16x16px Food Items" by maruki   (CC0 1.0) 16x16 像素食物
#   4) OpenGameArt  - "Food Pixel Art (45 icons)" by Luca Pixel (CC0 1.0) 16x16
#
# 下载完成后由 tools/build_textures.py 做像素化与 Minecraft 化处理。
# 本机实测 kenney.nl / opengameart.org 均可直连。

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$out = Join-Path $PSScriptRoot 'downloads'
$extractRoot = Join-Path $out 'extracted'
New-Item -ItemType Directory -Force -Path $out | Out-Null

$assets = @(
    @{
        Name = 'kenney_pixel-platformer-food-expansion'
        Url  = 'https://kenney.nl/media/pages/assets/pixel-platformer-food-expansion/76330de2bf-1696596511/kenney_pixel-platformer-food-expansion.zip'
        From = 'Kenney.nl'
        Lic  = 'CC0 1.0'
    }
    @{
        Name = 'oga_16x16px_food_items'
        Url  = 'https://opengameart.org/sites/default/files/Foodies_0.zip'
        From = 'OpenGameArt (maruki)'
        Lic  = 'CC0 1.0'
    }
    @{
        Name = 'oga_food_pixel_art_45'
        Url  = 'https://opengameart.org/sites/default/files/food_pixel_art.zip'
        From = 'OpenGameArt (Luca Pixel)'
        Lic  = 'CC0 1.0'
    }
)

$report = @()
foreach ($a in $assets) {
    $zip = Join-Path $out ($a.Name + '.zip')
    Write-Output ('downloading ' + $a.Name)
    & curl.exe -sSL --max-time 90 -o $zip $a.Url
    if (-not (Test-Path $zip)) {
        Write-Output '  -> FAILED'
        continue
    }
    $len = (Get-Item $zip).Length
    if ($len -lt 1000) {
        Write-Output ('  -> too small (' + $len + ' bytes), likely an error page; skipping')
        continue
    }
    Write-Output ('  -> ' + $len + ' bytes')

    $sub = Join-Path $extractRoot $a.Name
    New-Item -ItemType Directory -Force -Path $sub | Out-Null
    $z = [System.IO.Compression.ZipFile]::OpenRead($zip)
    try {
        foreach ($entry in $z.Entries) {
            if (-not $entry.Name) { continue }
            $target = Join-Path $sub $entry.FullName
            $dir = Split-Path -Parent $target
            if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
            [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $target, $true)
        }
    } finally {
        $z.Dispose()
    }
    $pngs = (Get-ChildItem $sub -Recurse -File -Filter *.png).Count
    Write-Output ('  -> extracted, ' + $pngs + ' png')
    $report += [pscustomobject]@{ Name = $a.Name; Source = $a.From; License = $a.Lic; Png = $pngs }
}

Write-Output ''
Write-Output '--- summary ---'
$report | Format-Table -AutoSize | Out-String -Width 200 | Write-Output

Write-Output '--- sample png files ---'
Get-ChildItem $extractRoot -Recurse -File -Filter *.png |
    Select-Object -First 40 |
    ForEach-Object { Write-Output ($_.FullName.Substring($extractRoot.Length + 1)) }
