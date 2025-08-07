; NSIS Installer Script for VinnyPix Typing Tools
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "WinVer.nsh"
!include "nsDialogs.nsh"

; General
Name "VinnyPix Typing Tools"
!define OUT_DIR ".."  ; Go up one level from the script directory
!define INSTALLER_NAME "VinnyPixTypingTools_Setup.exe"
OutFile "${OUT_DIR}\\${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES\VinnyPix\Typing Tools"
InstallDirRegKey HKLM "Software\VinnyPix\Typing Tools" "Install_Dir"
RequestExecutionLevel admin

; UI Configuration
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\VinnyPixTypingTools.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run VinnyPix Typing Tools"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View README"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; Variables
Var PythonInstalled
Var PythonPath
Var TesseractInstalled
Var CurrentUser
Var UserDocuments
Var UserPictures

; Custom Pages
Page custom PythonInstallPage
Page custom TesseractInstallPage

; Python Installation Page
Function PythonInstallPage
    ${If} $PythonInstalled == "1"
        Abort
    ${EndIf}
    
    nsDialogs::Create 1018
    Pop $0
    ${NSD_CreateLabel} 0 0 100% 24u "Python 3.10.11 Installation"
    Pop $0
    
    ${NSD_CreateLabel} 0 30u 100% 48u "VinnyPix Typing Tools requires Python 3.10.11. The installer will now download and install Python 3.10.11. $$
This will add Python to your system PATH and install it for all users. $$
Click Next to continue with the installation."
    Pop $0
    
    nsDialogs::Show
FunctionEnd

; Tesseract Installation Page
Function TesseractInstallPage
    ${If} $TesseractInstalled == "1"
        Abort
    ${EndIf}
    
    nsDialogs::Create 1018
    Pop $0
    ${NSD_CreateLabel} 0 0 100% 24u "Tesseract OCR Installation"
    Pop $0
    
    ${NSD_CreateLabel} 0 30u 100% 48u "VinnyPix Typing Tools requires Tesseract OCR for text recognition.$$
The installer will now download and install Tesseract OCR 5.3.0.$$
Click Next to continue with the installation."
    Pop $0
    
    nsDialogs::Show
FunctionEnd

Function .onInit
    ; Get current Windows username
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 == "Admin"
        UserInfo::GetName
    ${Else}
        ReadEnvStr $CurrentUser USERNAME
    ${EndIf}
    Pop $CurrentUser
    
    ; Get user documents and pictures folders
    SetShellVarContext current
    StrCpy $UserDocuments "$DOCUMENTS\VinnyPixTypingTools"
    StrCpy $UserPictures "$PICTURES\VinnyPixTypingTools-Pictures"
    
    ; Check Python installation
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
    ${If} $0 != ""
        StrCpy $PythonInstalled "1"
        StrCpy $PythonPath "$0python.exe"
    ${Else}
        StrCpy $PythonInstalled "0"
    ${EndIf}
    
    ; Check Tesseract installation
    ReadRegStr $0 HKLM "SOFTWARE\Tesseract-OCR" "InstallDir"
    ${If} $0 != ""
        StrCpy $TesseractInstalled "1"
    ${Else}
        StrCpy $TesseractInstalled "0"
    ${EndIf}
FunctionEnd

; Download and install Python 3.10.11
Function InstallPython
    ${If} $PythonInstalled == "1"
        Return
    ${EndIf}
    
    SetOutPath "$TEMP"
    NSISdl::download https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe "$TEMP\python-3.10.11-amd64.exe"
    Pop $0
    ${If} $0 != "success"
        MessageBox MB_ICONSTOP "Failed to download Python 3.10.11. Please install it manually and run the installer again."
        Abort
    ${EndIf}
    
    ExecWait '"$TEMP\python-3.10.11-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0' $0
    ${If} $0 != 0
        MessageBox MB_ICONSTOP "Failed to install Python 3.10.11. Error: $0"
        Abort
    ${EndIf}
    
    ; Update Python path
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
    StrCpy $PythonPath "$0python.exe"
    StrCpy $PythonInstalled "1"
    
    ; Install required packages
    nsExec::ExecToLog '"$PythonPath" -m pip install --upgrade pip'
    nsExec::ExecToLog '"$PythonPath" -m pip install -r "$INSTDIR\requirements.txt"'
FunctionEnd

; Download and install Tesseract OCR
Function InstallTesseract
    ${If} $TesseractInstalled == "1"
        Return
    ${EndIf}
    
    ; Check if Tesseract is already installed in common locations
    StrCpy $R0 "$PROGRAMFILES\Tesseract-OCR\tesseract.exe"
    IfFileExists "$R0" tesseract_found
    
    StrCpy $R0 "$PROGRAMFILES32\Tesseract-OCR\tesseract.exe"
    IfFileExists "$R0" tesseract_found
    
    StrCpy $R0 "$LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
    IfFileExists "$R0" tesseract_found
    
    ; If not found, download and install it
    SetOutPath "$TEMP"
    NSISdl::download https://github.com/UB-Mannheim/tesseract/wiki/tesseract-ocr-w64-setup-5.3.0.20221222.exe "$TEMP\tesseract-ocr-installer.exe"
    Pop $0
    ${If} $0 != "success"
        MessageBox MB_ICONSTOP "Failed to download Tesseract OCR. Please install it manually and run the installer again."
        Abort
    ${EndIf}
    
    ; Install Tesseract for all users (requires admin)
    ClearErrors
    ExecWait '"$TEMP\tesseract-ocr-installer.exe" /S /D=$PROGRAMFILES\Tesseract-OCR' $0
    ${If} ${Errors} OR $0 != 0
        ; Try installing in Program Files (x86)
        ExecWait '"$TEMP\tesseract-ocr-installer.exe" /S /D=$PROGRAMFILES32\Tesseract-OCR' $0
        ${If} ${Errors} OR $0 != 0
            ; Try installing in local app data
            ExecWait '"$TEMP\tesseract-ocr-installer.exe" /S /D=$LOCALAPPDATA\Programs\Tesseract-OCR' $0
            ${If} ${Errors} OR $0 != 0
                MessageBox MB_ICONSTOP "Failed to install Tesseract OCR. Error: $0. Please install it manually."
                Abort
            ${EndIf}
            StrCpy $R0 "$LOCALAPPDATA\Programs\Tesseract-OCR"
        ${Else}
            StrCpy $R0 "$PROGRAMFILES32\Tesseract-OCR"
        ${EndIf}
    ${Else}
        StrCpy $R0 "$PROGRAMFILES\Tesseract-OCR"
    ${EndIf}
    
    tesseract_found:
    ; Add Tesseract to system PATH if not already there
    ReadEnvStr $R1 "Path"
    ${StrContains} $R2 "$R0" "$R1"
    ${If} $R2 == ""
        ; Add to system PATH
        EnVar::SetHKLM
        EnVar::AddValue "Path" "$R0"
        
        ; Also add to current process environment
        System::Call 'Kernel32::SetEnvironmentVariable(t "Path", t "$R1;$R0")'
    ${EndIf}
    
    ; Set TESSDATA_PREFIX environment variable
    ${If} ${FileExists} "$R0\tessdata"
        System::Call 'Kernel32::SetEnvironmentVariable(t "TESSDATA_PREFIX", t "$R0\\tessdata")'
    ${EndIf}
    
    StrCpy $TesseractInstalled "1"
    
    ; Create a config file with the Tesseract path for the application
    FileOpen $R2 "$INSTDIR\tesseract_path.txt" w
    FileWrite $R2 "$R0\\tesseract.exe"
    FileClose $R2
    
    ; Also create a Python config file for the application
    FileOpen $R2 "$INSTDIR\tesseract_config.py" w
    FileWrite $R2 "import os$\n"
    FileWrite $R2 "TESSERACT_CMD = r'$R0\\\\tesseract.exe'$\n"
    FileWrite $R2 "TESSDATA_PREFIX = r'$R0\\\\tessdata'$\n"
    FileWrite $R2 "os.environ['TESSDATA_PREFIX'] = TESSDATA_PREFIX$\n"
    FileClose $R2
    
    ; Verify installation
    nsExec::ExecToStack '"$R0\\tesseract.exe" --version'
    Pop $0
    Pop $1
    ${If} $0 != 0
        MessageBox MB_ICONEXCLAMATION "Tesseract installation verification failed. The application might not work correctly.$\n$\nOutput: $1"
    ${EndIf}
FunctionEnd

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    ; Create required directories
    CreateDirectory "$UserDocuments"
    CreateDirectory "$UserPictures"
    
    ; Install Python if needed
    Call InstallPython
    
    ; Install Tesseract OCR if needed
    Call InstallTesseract
    
    ; Install application files
    File "dist\VinnyPixTypingTools.exe"
    File "icon.ico"
    File "LICENSE.txt"
    File "README.txt"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\VinnyPix"
    CreateShortCut "$SMPROGRAMS\VinnyPix\VinnyPix Typing Tools.lnk" "$INSTDIR\VinnyPixTypingTools.exe" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\VinnyPix\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\VinnyPix Typing Tools.lnk" "$INSTDIR\VinnyPixTypingTools.exe" "" "$INSTDIR\icon.ico"
    
    ; Add uninstall information
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "DisplayName" "VinnyPix Typing Tools"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "DisplayIcon" '"$INSTDIR\icon.ico"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "Publisher" "VinnyPix"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "DisplayVersion" "1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools" "NoRepair" 1
    
    ; Create registry key for Tesseract-OCR path
    WriteRegStr HKLM "SOFTWARE\VinnyPix\Typing Tools" "Install_Dir" "$INSTDIR"
SectionEnd

Section "Uninstall"
    ; Show confirmation message
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove VinnyPix Typing Tools?$$
Note: Your configuration and data files will be kept." IDYES proceed_with_uninstall
    Abort
    
    proceed_with_uninstall:
    
    ; Remove application files
    Delete "$INSTDIR\VinnyPixTypingTools.exe"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$INSTDIR\icon.ico"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\README.txt"
    
    ; Remove any remaining files in the installation directory
    Delete "$INSTDIR\*.*"
    
    ; Remove shortcuts
    SetShellVarContext all
    Delete "$SMPROGRAMS\VinnyPix\VinnyPix Typing Tools.lnk"
    Delete "$SMPROGRAMS\VinnyPix\Uninstall.lnk"
    Delete "$DESKTOP\VinnyPix Typing Tools.lnk"
    
    ; Remove directories
    RMDir "$SMPROGRAMS\VinnyPix"
    RMDir /r "$INSTDIR\_internal"
    RMDir "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VinnyPixTypingTools"
    DeleteRegKey /ifempty HKLM "SOFTWARE\VinnyPix\Typing Tools"
    
    ; Note: We don't uninstall Python or Tesseract as they might be used by other applications
    
    ; Show message about remaining files
    SetShellVarContext current
    MessageBox MB_ICONINFORMATION|MB_OK "VinnyPix Typing Tools has been uninstalled. $$
        $$
        Note: The following directories were not removed to preserve your data:$$
        - $DOCUMENTS\VinnyPixTypingTools$$
        - $PICTURES\VinnyPixTypingTools-Pictures$$
        $$
        You can delete these folders manually if you don't need the data anymore."
SectionEnd
