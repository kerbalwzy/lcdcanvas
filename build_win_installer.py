import subprocess


def create_inno_installer():
    try:
        subprocess.run([
            r"C:/Program Files (x86)/Inno Setup 6/ISCC.exe",  
            "/dBuildDir=build\main.dist",
            "installer_win.iss"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Inno Setup create fail: {e}")

if __name__ == "__main__":
    create_inno_installer()