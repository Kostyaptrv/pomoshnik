$InnoPath = "C:\Program Files (x86)\Inno Setup 7\ISCC.exe"
$ProjectPath = "C:\Users\kot35\IdeaProjects\pomoshnik"

Write-Host "Checking Inno Setup..."
if (Test-Path $InnoPath) {
    Write-Host "Found: $InnoPath"
    Set-Location $ProjectPath
    Write-Host "Building installer..."
    & $InnoPath "installer.iss"
    Write-Host "Done!"
} else {
    Write-Host "Inno Setup not found at: $InnoPath"
    Write-Host "Searching for ISCC.exe..."
    $found = Get-ChildItem "C:\" -Recurse -Filter "ISCC.exe" -ErrorAction SilentlyContinue | Select-Object -First 5
    if ($found) {
        foreach ($item in $found) {
            Write-Host "Found: $($item.FullName)"
        }
    } else {
        Write-Host "ISCC.exe not found anywhere on C:\"
    }
}
