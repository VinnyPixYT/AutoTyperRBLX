import PyInstaller.__main__
import shutil
import os
import sys
import subprocess
import tempfile
import urllib.request

def build_application():
    print("Cleaning up previous builds...")
    # Clean up previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('VinnyPixTypingTools.spec'):
        os.remove('VinnyPixTypingTools.spec')
    
    # Check if icon file exists
    icon_path = os.path.join('internal', 'icon.ico')
    icon_arg = f'--icon={icon_path}' if os.path.exists(icon_path) else ''
    
    # Create necessary directories
    os.makedirs('dist', exist_ok=True)
    
    # Ensure Tesseract config file exists
    tesseract_config_path = os.path.join('internal', 'tesseract_config.py')
    if not os.path.exists(tesseract_config_path):
        print("Tesseract config not found. Creating default config...")
        with open(tesseract_config_path, 'w') as f:
            f.write("""import os
# Default Tesseract paths (will be overridden by installer)
TESSERACT_CMD = r'tesseract'  # Will be updated by the installer
TESSDATA_PREFIX = ''  # Will be updated by the installer
""")
    
    print("Building application...")
    # Package the application
    cmd = [
        os.path.join('internal', 'scaryspelling_autotyper.py'),
        '--onefile',
        '--windowed',
        '--name=VinnyPixTypingTools',
        '--noconsole',
        '--clean',
        '--add-data=internal/icon.ico;internal' if os.path.exists(icon_path) else '',
        '--add-data=internal/tesseract_config.py;internal',
        '--hidden-import=pytesseract',
        '--hidden-import=pyautogui',
        '--hidden-import=keyboard',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=win32gui',
        '--hidden-import=win32con',
        '--hidden-import=win32api'
    ]
    
    # Add icon if it exists
    if icon_arg:
        cmd.append(icon_arg)
    
    # Filter out any empty strings from the command list
    cmd = [arg for arg in cmd if arg]
    
    print("Running PyInstaller with command:", ' '.join(cmd))
    
    # Run PyInstaller with the constructed command
    PyInstaller.__main__.run(cmd)
    
    print("\nBuild complete! Executable is in the 'dist' folder.")

if __name__ == "__main__":
    build_application()
