; ============================================
; Инсталлятор: Помощник для написания песен
; ============================================

#define MyAppName "Помощник для написания песен"
#define MyAppVersion "1.0"
#define MyAppPublisher "Pomoshnik Dev"
#define MyAppExeName "Помощник.exe"

[Setup]
; Основная информация
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright="© 2025 {#MyAppPublisher}"
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=Помощник_установщик_1.0
SetupIconFile=app_icon.ico

; Настройки установки
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin

[Files]
; Основной исполняемый файл и все зависимости из dist
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Ярлык в группу меню "Программы"
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\{#MyAppName} (Портативный)"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"

; Ярлык на рабочий стол
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"

; Ярлык в панель быстрого доступа
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"

[Uninstall]
Delete: {app}\*

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
