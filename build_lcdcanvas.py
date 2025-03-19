import subprocess
from app.consts import APP_NAME

AppName = f"{APP_NAME}.exe"
ProductName = r"LCD CANVAS"
ProductVersion = r"1.0.0.2"
FileVersion = r"1.0.0.2"
FileDescription = r"LCD CANVAS"
CopyRight = r"Copyright (c) 2025 lcdcanvas.com"

nuitka_command = [
    ".venv/Scripts/python.exe",
    "-m",
    "nuitka",
    "--standalone",
    "--windows-icon-from-ico=static/favicon.ico",
    "--windows-console-mode=disable", # disbale console
    "--windows-uac-admin",  # require admin
    "--include-package=encodings",  
    "--include-module=codecs",  
    "--include-module=locale",  
    "--plugin-enable=upx",  # enable upx
    # add dlls, must be specified file
    "--include-data-files=libs/lhm/LibreHardwareMonitorLib.dll=libs/lhm/LibreHardwareMonitorLib.dll",  
    "--include-data-files=libs/lhm/HidSharp.dll=libs/lhm/HidSharp.dll", 
    "--include-data-files=themes/DemoTheme.json=themes/DemoTheme.json",
    # add data dirs
    "--include-data-dir=libs/lhm=libs/lhm",
    "--include-data-dir=static=static",
    # version info
    f"--product-name={ProductName}",
    f"--product-version={ProductVersion}",
    f"--file-version={FileVersion}",
    f"--file-description={FileDescription}",
    f"--copyright={CopyRight}",
    "main.py",
    "--output-dir=build",
    f"--output-filename={AppName}",
]

if __name__ == "__main__":
    try:
        subprocess.run(nuitka_command, check=True)
        print("Nuitka compilation completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Nuitka compilation failed: {e}".format(e=e))
