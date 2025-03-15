# system tray icon
import logging
import os
import time
import webbrowser
import win32api  # type: ignore
import win32con  # type: ignore
import win32gui  # type: ignore
from app import consts
from app.ui import UIWindowManager
from app.hardware_monitor.monitor import hardware_monitor_api
from app.i18n import t

logger = logging.getLogger()

class SysTrayIcon:

    def __init__(self, icon, hover_text):
        self.hover_text = hover_text
        self.icon = icon
        self.hwnd = None
        self.notify_id = None

    def show_icon(self):
        message_map = {
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER + 20: self.on_notify,
        }  # add your message map here

        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = self.hover_text
        wc.lpfnWndProc = message_map
        class_atom = win32gui.RegisterClass(wc)

        self.hwnd = win32gui.CreateWindow(
            class_atom, self.hover_text, 0, 0, 0, 0, 0, 0, 0, hinst, None
        )

        # use custom icon
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(
            hinst, self.icon, win32con.IMAGE_ICON, 0, 0, icon_flags
        )

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        self.notify_id = (
            self.hwnd,
            0,
            flags,
            win32con.WM_USER + 20,
            hicon,
            self.hover_text,
        )
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self.notify_id)

    def on_notify(self, hwnd, msg, wparam, lparam):
        try:
            if lparam == win32con.WM_LBUTTONUP:
                UIWindowManager.hw_monitor_window().show()
                UIWindowManager.hw_monitor_window().restore()
            elif lparam == win32con.WM_RBUTTONUP:
                self.show_menu()
        except Exception as e:
            logger.error(e, stack_info=True)
        return 0

    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(
            menu, win32con.MF_STRING, consts.SYSTRAY_HARDWARE_MONITOR_MENU_ID, t("label.HardwareMonitor")
        )
        win32gui.AppendMenu(
            menu, win32con.MF_STRING, consts.SYSTRAY_THEME_EDITOR_MENU_ID, t("label.ThemeEditor")
        )
        win32gui.AppendMenu(
            menu, win32con.MF_STRING, consts.SYSTRAY_EXIT_MENU_ID, t("label.Quite")
        )
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(
            menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None
        )
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def on_command(self, hwnd, msg, wparam, lparam):
        if wparam == consts.SYSTRAY_EXIT_MENU_ID:
            # close the lcd display thread
            hardware_monitor_api.toggleDisplay(False)
            # close all windows
            UIWindowManager.close_all_windows()
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.2)
            os._exit(0)
        if wparam == consts.SYSTRAY_HARDWARE_MONITOR_MENU_ID:
            UIWindowManager.hw_monitor_window().show()
            UIWindowManager.hw_monitor_window().restore()
        if wparam == consts.SYSTRAY_THEME_EDITOR_MENU_ID:
            webbrowser.open_new_tab("https://lcdcanvas.com/themeeditor")
        return 0

    def on_destroy(self, hwnd, msg, wparam, lparam):
        # clean up and exit
        if self.notify_id:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self.notify_id)
            self.notify_id = None
        win32gui.PostQuitMessage(0)
        return 0
