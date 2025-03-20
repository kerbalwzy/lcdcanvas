[Setup]
AppName=LCDCANVAS
AppVersion=1.0.0.3
DefaultDirName={autopf}\LCDCANVAS
OutputDir=dist
OutputBaseFilename=lcdcanvas_1.0.0.3_Setup
SetupIconFile=static\favicon.ico
PrivilegesRequired=admin

[Files]
Source: "build\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commondesktop}\LCDCANVAS"; Filename: "{app}\LCDCANVAS.exe"; IconFilename: "{app}\static\favicon.ico"

[Run]
Filename: "{app}\LCDCANVAS.exe"; Description: "Startup"; Flags: shellexec postinstall nowait

[Code]

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  UninstallExe: String;
begin
  if CheckForMutexes('LCDCANVAS') then
  begin
    Log('Detected a running process');
    if Exec('taskkill', '/f /im LCDCANVAS.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      Log('Successfully terminated the process')
    else
      Log('Failed to terminate the process, error code: ' + IntToStr(ResultCode));
  end
  else
  begin
    Log('No running process detected');
  end;

  // Check if an old version is installed
  if RegKeyExists(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\lcdcavans_is1') then
  begin
    Log('Detected an old version installation');
    // Get the uninstaller path
    if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\lcdcavans_is1', 'UninstallString', UninstallExe) then
    begin
      Log('Successfully obtained the uninstaller path: ' + UninstallExe);
      // Perform a silent uninstall
      if Exec(RemoveQuotes(UninstallExe), '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
        Log('Successfully executed the uninstaller')
      else
        Log('Failed to execute the uninstaller, error code: ' + IntToStr(ResultCode));
    end
    else
    begin
      Log('Failed to obtain the uninstaller path');
    end;
    
    // Delete residual files
    if DelTree(ExpandConstant('{autopf}\LCDCANVAS'), True, True, True) then
      Log('Successfully deleted residual files')
    else
      Log('Failed to delete residual files');
  end
  else
  begin
    Log('No old version installation detected');
  end;

  Log('InitializeSetup execution completed');
  Result := True;
end;