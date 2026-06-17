# Copy landing images from Django staticfiles into Vercel public/static/
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root "staticfiles"
$dest = Join-Path $root "AiG landing page\templates\public\static"

if (-not (Test-Path $src)) {
    Write-Host "No staticfiles folder found at: $src"
    exit 1
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null
$images = Get-ChildItem $src -Recurse -File -Include *.png,*.jpg,*.webp,*.jpeg,*.gif
if (-not $images) {
    Write-Host "No images found in staticfiles. Add images to public/static manually."
    exit 1
}

foreach ($img in $images) {
    if ($img.DirectoryName -match '\\admin\\') { continue }
    Copy-Item $img.FullName -Destination (Join-Path $dest $img.Name) -Force
    Write-Host "Copied $($img.Name)"
}

Write-Host "Done. $($images.Count) file(s) processed."
