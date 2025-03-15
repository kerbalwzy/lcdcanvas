# coding:utf-8
import os
import sys

APP_NAME = "LCDCANVAS" # no space or special character in name !!!
IS_EXE = not sys.argv[0].lower().endswith(".py")
if IS_EXE:
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
SETTING_PATH = os.path.join(BASE_DIR, "settings.json")
LOG_PATH = os.path.join(BASE_DIR, "log.txt")
LOG_LEVEL = "DEBUG"
THEMES_SOURCE_DIR = os.path.join(BASE_DIR, "themes")
THEMES_DIR = os.path.join(BASE_DIR, "themes")
STATIC_DIR = os.path.join(BASE_DIR, "static")
LOGO_PATH = os.path.join(STATIC_DIR, "favicon.ico")
#
LIBS_DIR = os.path.join(BASE_DIR, "libs")
LHM_LHMONITOR_DLL_PATH = os.path.join(LIBS_DIR, "lhm/LibreHardwareMonitorLib.dll")
LHM_HIDSHARP_DLL_PATH = os.path.join(LIBS_DIR, "lhm/HidSharp.dll")
#
SYSTRAY_EXIT_MENU_ID = 0x00
SYSTRAY_HARDWARE_MONITOR_MENU_ID = 0x01
SYSTRAY_THEME_EDITOR_MENU_ID = 0x02
#
UI_PATH = os.path.join(STATIC_DIR, "index.html")
UI_MONITOR_URL = f"file:///{UI_PATH}#/hwmonitor"
THEME_DRAWER_URL = f"file:///{UI_PATH}#/themeplayer"


#
HOME_DIR = os.path.join(os.path.expanduser("~"), f".{APP_NAME}")
if IS_EXE:
    LOG_LEVEL = "INFO"
    THEMES_DIR = os.path.join(HOME_DIR, "themes")

def init_dir():
    os.makedirs(HOME_DIR, exist_ok=True)
    os.makedirs(THEMES_DIR, exist_ok=True)


def print_consts():
    print(f"APP_NAME:\t{APP_NAME}")
    print(f"IS_EXE:\t{IS_EXE}")
    print(f"LOG_LEVEL:\t{LOG_LEVEL}")
    print(f"LOG_PATH:\t{LOG_PATH}")
    print(f"SETTING_PATH:\t{SETTING_PATH}")
    print(f"THEMES_DIR:\t{THEMES_DIR}")
    print(f"STATIC_DIR:\t{STATIC_DIR}")
    print(f"LIBS_DIR:\t{LIBS_DIR}")
    print(f"THEMES_SOURCE_DIR:\t{THEMES_SOURCE_DIR}")


init_dir()
print_consts()
