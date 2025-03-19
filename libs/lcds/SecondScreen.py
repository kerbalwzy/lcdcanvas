# Any secondary screen can find by pywebview.screens

import logging
from typing import List
import webview
from PIL import Image
from libs.lcds._base import LCD, hide_window_from_taskbar, image_to_base64

logger = logging.getLogger()


class LCD_2ndScreen(LCD):
    # Create a simple HTML page with a body background image
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>2ndScreen</title>
        <style>
            /* 设置 html 和 body 元素的高度为 100% */
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            body {
                overflow: hidden;
                /* 设置背景图片铺满整个屏幕 */
                background-size: 100% 100%;
                background-position: center;
                background-repeat: no-repeat;
            }
        </style>
    </head>
    <body>
        <script>
            function updateImage(src) {
                document.body.style.backgroundImage = `url(${src})`;
            }
        </script>
    </body>
    </html>
    """

    def __init__(self, index: int, width: int, height: int, x: int, y: int):
        self.name = f"2ndScreen #{index+1}"
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.__window = None

    def __init_window(self) -> webview.Window:
        self.__window = webview.create_window(
            title=self.name,
            html=self.html,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            fullscreen=True,
            resizable=False,
            frameless=True,
            on_top=True,
        )
        logger.debug(f"Create {self.name} window")
        return self.__window

    def unique_id(self) -> str:
        return self.name

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
            self.__window.destroy()
            self.__window = None
            logger.debug(f"Destroy {self.name} window")

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
        if self.__window is None:
            self.__init_window()
            hide_window_from_taskbar(self.__window.title)
        imgsrc = image_to_base64(image=img)
        self.__window.evaluate_js(f"updateImage('{imgsrc}')")

    def clear(self) -> None:
        # not support
        pass

    def set_brightness(self, brightness: int) -> None:
        # not support
        pass

    def __str__(self) -> str:
        return self.name


__2nd_screen_cache = {}


def find_2nd_screen() -> List[LCD_2ndScreen]:
    screens = webview.screens
    if len(screens) == 1:
        return []
    res = []
    # exclude the first screen, it is the primary screen
    for i, s in enumerate(screens[1:]):
        cache_key = f"{s.width}-{s.height}-{s.x}-{s.y}"
        cache_screen = __2nd_screen_cache.get(cache_key, None)
        if cache_screen is None:
            cache_screen = LCD_2ndScreen(
                index=i, width=s.width, height=s.height, x=s.x, y=s.y
            )
            __2nd_screen_cache[cache_key] = cache_screen
        res.append(cache_screen)
    return res
