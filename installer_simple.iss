; ============================================
; Инсталлятор: Pomoshnik - Song Writing Helper
; ============================================

#define MyAppName "Pomoshnik"
#define MyAppVersion "1.0"
#define MyAppPublisher "Pomoshnik Dev"
#define MyAppExeName "Pomoshnik.exe"

[Setup]
; Main info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567891}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright="© 2026 {#MyAppPublisher}"
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=Pomoshnik_Setup_1.0
SetupIconFile=app_icon.ico

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Files]
; Copy all files from dist folder
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu icon
Name: "{group}\{#MyAppName}"; Filename: "{app}\Помощник.exe"

; Desktop icon
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\Помощник.exe"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
