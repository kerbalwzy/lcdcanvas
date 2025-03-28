# coding:utf-8
import logging
import webview
import win32api  # type: ignore
import win32con  # type: ignore
from app import consts
from app.i18n import t
from app.setting import settings


logger = logging.getLogger()


class UIWindowManager:
    ThemePlayerWindow: webview.Window = None
    HWMonitorWindow: webview.Window = None

    @classmethod
    def close_all_windows(cls):
        while len(webview.windows) > 0:
            window = webview.windows.pop()
            window.destroy()

    @classmethod
    def hw_monitor_window(cls) -> webview.Window:
        if cls.HWMonitorWindow is not None:
            return cls.HWMonitorWindow

        from app.hardware_monitor.monitor import hardware_monitor_api

        main_screen = webview.screens[0]
        window_width = 1024
        window_height = 666
        # Center the window on the main screen
        x = (main_screen.width - window_width) // 2
        y = (main_screen.height - window_height) // 2
        window = webview.create_window(
            title=t("label.HardwareMonitor"),
            url=consts.UI_MONITOR_URL,
            width=window_width,
            height=window_height,
            x=x,
            y=y,
            js_api=hardware_monitor_api,
            resizable=False,
        )
        window.events.closed += cls._on_window_closed(window=window)
        cls.HWMonitorWindow = window
        logger.debug("Create HWMonitor window success")
        return window

    @classmethod
    def theme_player_window(cls) -> webview.Window:
        if cls.ThemePlayerWindow is not None:
            return cls.ThemePlayerWindow
        # Create a hidden window to play theme
        from app.hardware_monitor.theme import theme_player_api

        window = webview.create_window(
            title="ThemePlayerHiddenWindow",
            url=consts.THEME_DRAWER_URL,
            js_api=theme_player_api,
            hidden=True,
            frameless=True,
            resizable=False,
            on_top=True,
            easy_drag=True,
        )
        window.events.closing += cls._on_window_closing(window=window)
        cls.ThemePlayerWindow = window
        logger.debug("Create ThemePlayer window success")
        return window

    @classmethod
    def _on_window_closing(cls, window: webview.Window):
        def func():
            if window == cls.ThemePlayerWindow:
                # Use hidden instead of close to prevent window from closing
                cls.ThemePlayerWindow.hidden = True
                cls.ThemePlayerWindow.hide()
                logger.warning("ThemePlayer window hidden instead of close")
                return False  # return False to prevent window from closing

        return func

    @classmethod
    def _on_window_closed(cls, window: webview.Window):
        def func():
            if window == cls.HWMonitorWindow:
                cls.HWMonitorWindow = None
            logger.warning(f"Window <{window.title}> closed")

        return func


class UIAPIBase:

    def showerror(self, msg: str):
        win32api.MessageBox(0, msg, t("label.Error"), win32con.MB_ICONERROR)

    def showwarning(self, msg: str):
        win32api.MessageBox(0, msg, t("label.Warning"), win32con.MB_ICONWARNING)

    def showinfo(self, msg: str):
        win32api.MessageBox(0, msg, t("label.Info"), win32con.MB_ICONINFORMATION)

    def askyesno(self, title, msg) -> bool:
        result = win32api.MessageBox(
            0, msg, title, win32con.MB_YESNO | win32con.MB_ICONQUESTION
        )
        return result == win32con.IDYES

    def setLanguageLocale(self, locale: str):
        t.set_locale(locale)
        settings.set_monitor_settings({"lang": locale})
        logger.debug(f"Set language locale to <{locale}>")
        # clean weather cache data
        from app.hardware_monitor.sensors import weather

        weather.clean_cache()
