import logging
import locale
import threading
import traceback
import win32gui  # type: ignore
import win32api  # type: ignore
import win32con  # type: ignore
import webview
from logging.handlers import RotatingFileHandler

# Upgrade logging level for some modules
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("pywebview").setLevel(logging.ERROR)
logging.getLogger("comtypes").setLevel(logging.ERROR)
logging.getLogger("comtypes._post_coinit.unknwn").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

# Import all app modules
try:
    from app.consts import LOG_PATH, LOG_LEVEL, APP_NAME, LOGO_PATH, IS_EXE
    from app.systray import SysTrayIcon
    from app.ui import UIWindowManager
    from app.util import (
        require_runas_admin,
        require_runas_unique,
        copy_theme_to_user_dir,
    )

except Exception as e:
    stack_trace = traceback.format_exc()
    win32api.MessageBox(0, stack_trace, "RuntimeEnvError", win32con.MB_ICONERROR)
    exit(1)

# global logger configuration
# use current locale for date/time formatting in logs
locale.setlocale(locale.LC_ALL, "")
logging.basicConfig(  # format='%(asctime)s [%(levelname)s] %(message)s in %(pathname)s:%(lineno)d',
    format="%(asctime)s %(pathname)s:%(lineno)d\t[%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(
            LOG_PATH, maxBytes=1000000, backupCount=1
        ),  # Log in textfile max 1MB
        logging.StreamHandler(),  # Log also in console
    ],
    datefmt="%x %X",
)

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
logger.info("Logger initialized")


def start_tray_icon():
    tray = SysTrayIcon(LOGO_PATH, APP_NAME)
    tray.show_icon()
    win32gui.PumpMessages()
    logger.info("Systray icon initialized")


def main():
    # Check run as admin
    require_runas_unique()
    require_runas_admin()
    # Copy theme files into user's home directory
    copy_theme_to_user_dir()
    # open the hidden window for theme player
    UIWindowManager.theme_player_window()
    # Start systray icon
    threading.Thread(
        target=start_tray_icon,
        daemon=True,
    ).start()
    # Start UI
    webview.start(
        func=UIWindowManager.hw_monitor_window,
        debug=not IS_EXE,
        # gui="edgechromium"
    )


if __name__ == "__main__":
    main()
