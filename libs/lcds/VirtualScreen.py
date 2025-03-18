# Virtual screen on decktop
import logging
import win32gui  # type: ignore
import win32con  # type: ignore
from PIL import Image
from libs.lcds.base import LCD
from app.ui import UIWindowManager

logger = logging.getLogger()


class LCD_VirtualScreen(LCD):

    def __init__(self):
        self.__window = None

    @classmethod
    def unique_id(cls) -> str:
        return "VirtualScreen"

    @classmethod
    def is_connected(cls) -> bool:
        # not support, always return True
        return True

    def open(self):
        # not support
        pass

    def is_open(self) -> bool:
        # not support, always return True
        return True

    def close(self):
        if self.__window is not None:
            self.__window.hide()
            self.__window.hidden = True
            logger.debug("Hide ThemePlayer window")

    def write(self, data: bytes):
        # not support
        pass

    def read(self, length: int) -> bytes:
        # not support
        pass

    def handshake(self):
        # not support
        pass

    def display(self, img: Image.Image):
        # show the image on the screen by ThemePlayer window

        if self.__window is None:
            self.__window = UIWindowManager.theme_player_window()
            hwnd = win32gui.FindWindow(None, self.__window.title)
            if hwnd:
                # Hide the window from the taskbar
                current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                new_style = (
                    current_style & ~win32con.WS_EX_APPWINDOW
                ) | win32con.WS_EX_TOOLWINDOW
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
            logger.debug("Hide ThemePlayer window from the taskbar")

        if self.__window.width != img.width or self.__window.height != img.height:
            logger.debug(f"Resize ThemePlayer window to {img.width}x{img.height}")
            self.__window.resize(img.width, img.height)

        if self.__window.hidden:
            self.__window.show()
            self.__window.hidden = False
            logger.debug("Show ThemePlayer window")

    def clear(self) -> None:
        # not support
        pass

    def set_brightness(self, brightness: int) -> None:
        # not support
        pass

    def __str__(self) -> str:
        return f"Virtual Screen"
