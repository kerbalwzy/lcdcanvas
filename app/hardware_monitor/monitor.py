"""
Configure the hardware monitor:
1. Connect to the selected screen.
2. Select the hardware status data display theme.
3. Set the screen brightness.
4. Set the screen display rotation angle.
"""

import json
import logging
import os
import threading
import time
from typing import List
from app import consts
from app.i18n import t
from app.ui import UIAPIBase
from app.setting import settings
from app.ui import UIWindowManager
from app.util import del_win_startup, image_from_base64, set_win_startup
from app.hardware_monitor.sensors import SensorsMap, weather
from libs.lcds import LCD, find_connected_screens, lcd_virtual_screen

__all__ = ["hardware_monitor_api"]

logger = logging.getLogger()
DisplayLock = threading.Lock()


class HardwareMonitorAPI(UIAPIBase):

    def __init__(self) -> None:
        self.__lcd: LCD = None
        self.__settings = settings
        self.__brightness = 100
        self.__rotation = 0
        self.__display = False
        self.__connected_screens = dict()

    def __del__(self) -> None:
        if self.__lcd:
            try:
                self.__lcd.close()
            except Exception as e:
                logger.error(e)

    def loadScreens(self) -> List[str]:
        """
        Get the list of available devices.
        """
        self.__connected_screens = find_connected_screens()
        res = list()
        for uid, screen in self.__connected_screens.items():
            uid: str
            screen: LCD
            res.append(
                {
                    "uid": uid,
                    "width": screen.width,
                    "height": screen.height,
                }
            )
        logger.debug(f"Get the list of available screens")
        return res

    def loadThemes(self) -> List[dict]:
        res = list()
        for filename in os.listdir(consts.THEMES_DIR):
            if not filename.endswith(".json"):
                continue
            item = dict()
            item["name"] = filename[:-5]
            filepath: str = os.path.join(consts.THEMES_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as fp:
                _theme = json.load(fp)
                item["shape"] = _theme["shape"]
                item["width"] = _theme.get("width", 0)
                item["height"] = _theme.get("height", 0)
                item["radius"] = _theme.get("radius", 0)
            res.append(item)
        res.sort(key=lambda x: x["name"])
        logger.debug(f"Get the list of available themes")
        return res

    def importTheme(self, content: str, filename: str) -> None:
        savepath = os.path.join(consts.THEMES_DIR, filename)
        if os.path.exists(savepath):
            if not self.askyesno(
                title=t("label.Warning"),
                msg=t("msg.ThemeFileSameNameReplace"),
            ):
                return
        with open(savepath, "w", encoding="utf-8") as fp:
            fp.write(content)
        self.showinfo(t("msg.ThemeFileImportSuccess"))

    def deleteTheme(self, filename: str) -> None:
        savepath = os.path.join(consts.THEMES_DIR, f"{filename}.json")
        if os.path.exists(savepath):
            os.remove(savepath)
            self.showinfo(t("msg.ThemeFileDeleteSuccess"))

    def selectScreen(self, uid: str) -> bool:
        # try to match a screen driver
        driver = self.__connected_screens.get(uid, None)
        with DisplayLock:
            if self.__lcd is not None:
                if self.__lcd.unique_id() == uid:
                    # If the same screen is selected, do nothing.
                    return True
                # Close the prev screen dirver
                try:
                    self.__lcd.close()
                except Exception:
                    pass
            # Set the new screen driver
            self.__lcd = driver
        # If selected screen, update the screen settings
        if self.__lcd:
            screen_settings = settings.get_screen_settings(uid)
            # Initialize the screen brightness and rotation angle.
            self.__brightness = screen_settings.get("brightness", 100)
            self.__rotation = screen_settings.get("rotation", 0)
            self.__set_brightness()
            logger.debug(f"Screen <{uid}> selected")
        else:
            logger.debug(f"Screen selected clean")
        # Update monitor settings
        settings.set_monitor_settings({"lastScreen": uid if driver else ""})
        return self.__lcd is not None

    def selectTheme(self, theme: str) -> str:
        theme_content = ""
        # Try to get the theme file content
        if theme:
            try:
                filepath: str = os.path.join(consts.THEMES_DIR, f"{theme}.json")
                with open(filepath, "r", encoding="utf-8") as fp:
                    theme_content: str = fp.read()
            except Exception as e:
                logger.error(e)
                self.showerror(t("msg.ThemeFileLoadFailed"))
                theme = ""
        # if there screen is selected, update the screen setting
        if self.__lcd:
            logger.debug(f"Update screen settings <lastTheme:{theme}>")
            settings.set_screen_settings(self.__lcd.unique_id(), {"lastTheme": theme})
        # async state to
        with DisplayLock:
            try:
                UIWindowManager.theme_player_window().evaluate_js(
                    f"window.loadTheme('{theme}')"
                )
            except Exception as e:
                logger.error(e)
        if theme:
            logger.debug(f"Theme <{theme}> selected")
        else:
            logger.debug(f"Theme selected clean")
        return theme_content

    def getScreenSettings(self, screen: str) -> dict:
        res = self.__settings.get_screen_settings(screen)
        logger.debug(f"Get the screen <{screen}> settings: {res}")
        return res

    def setScreenSettings(self, screen: str, settings: dict) -> None:
        self.__settings.set_screen_settings(screen, settings)
        # update screen settings
        self.__brightness = settings.get("brightness", 100)
        self.__rotation = settings.get("rotation", 0)
        self.__set_brightness()
        logger.debug(f"Set the screen <{screen}> settings: {settings}")

    def getMonitorSettings(self) -> dict:
        res = self.__settings.get_monitor_settings()
        logger.debug(f"Get the monitor settings: {res}")
        # add display state
        res["displayState"] = self.__display
        return res

    def setMonitorSettings(self, settings: dict) -> None:
        self.__settings.set_monitor_settings(settings)
        # update weather sensor
        weather_settings = settings.get("weather", {})
        weather.set_conf(**weather_settings)
        # update startup
        startup = settings.get("startup", False)
        self.__set_start_up(startup)
        logger.debug(f"Set the monitor settings: {settings}")

    def toggleDisplay(self, display: bool) -> None:
        """
        Switch the screen display.
        """
        if display:
            self.__start_display()
        else:
            self.__stop_display()
        logger.debug(f"Switch the screen display: {display}")

    def getSensorsValue(self, sensors: List[str]) -> dict:
        """
        Get the sensor data.
        """
        res = dict()
        for sensor in sensors:
            instance = SensorsMap.get(sensor, None)
            if instance:
                try:
                    res[sensor] = instance.status()
                except Exception as e:
                    logger.error(f"Sensor <{sensor}> error: {e}")
        # logger.debug(f"Get the sensor data: {sensors}")
        return res

    def __set_start_up(self, startup: bool) -> None:
        """
        Set whether to start up automatically.
        """
        monitorConf = self.__settings.get("monitor", {})
        monitorConf["startup"] = startup
        self.__settings.set("monitor", monitorConf)
        #
        if not consts.IS_EXE:
            return
        name = f"{consts.APP_NAME}_AutoStartup"
        exepath = f"{consts.BASE_DIR}\\{consts.APP_NAME}.exe"
        if startup:
            set_win_startup(name, exepath)
        else:
            del_win_startup(name)
        logger.info(f"Set startup on boot: {startup}")

    def __set_brightness(self) -> None:
        """
        Set the screen brightness.
        """
        for i in range(3):  # Try 3 times
            with DisplayLock:
                # Pessimistic lock to prevent UI thread blocking
                if not self.__lcd:
                    logger.debug("Screen not selected, set brightness failed.")
                    return
                try:
                    if not self.__lcd.is_open():
                        self.__lcd.open()
                    self.__lcd.set_brightness(self.__brightness)
                except Exception as e:
                    logger.error(e)
                    # Try to close the screen and retry
                    self.__lcd.close()
                    if i == 2:
                        self.showerror(t("msg.BrightnessSetFailed"))
                    time.sleep(1)
                else:
                    logger.debug(
                        f"Set the screen<{self.__lcd.unique_id()}> brightness: {self.__brightness}"
                    )
                    break

    def __display_loop(self) -> None:
        """
        Screen display loop.
        """
        if self.__display:  # Already displaying
            return
        self.__display = True
        error_limit = 10
        error_count = 0
        while self.__display and self.__lcd:
            try:
                start = time.time()
                if not self.__lcd.is_open():
                    with DisplayLock:
                        # Pessimistic lock to prevent UI thread blocking
                        if not (self.__display and self.__lcd):
                            break
                        self.__lcd.close()
                        self.__lcd.open()
                imgSrc = UIWindowManager.theme_player_window().evaluate_js(
                    "window.playerToImageSrc()"
                )
                if not imgSrc:
                    continue
                img = image_from_base64(imgSrc)
                if self.__lcd.unique_id() != lcd_virtual_screen.unique_id():
                    img = img.rotate(self.__rotation, expand=True)
                # Display the image
                with DisplayLock:
                    # Pessimistic lock to prevent UI thread blocking
                    if not (self.__display and self.__lcd):
                        break
                    self.__lcd.display(img)
                cost_time = time.time() - start
                logger.info(
                    f"Screen <{self.__lcd.unique_id()}> display succeeded. Time taken: {cost_time:.2f}s"
                )
            except Exception as e:
                logger.error(e)
                with DisplayLock:
                    # Pessimistic lock to prevent UI thread blocking
                    if not (self.__display and self.__lcd):
                        break
                    self.__lcd.close()
                error_count += 1
                if error_count > error_limit:
                    logger.warning(
                        "The number of screen display exceptions has reached the limit. Automatically exiting..."
                    )
                    self.showerror(t("msg.ScreenDisplayFailed"))
                    break
                logger.warning(f"Screen connection exception. Retrying...{error_count}")
                time.sleep(1)
            else:
                error_count = 0
                time.sleep(0.1 if cost_time > 1 else 1 - cost_time)

        self.__stop_display()

    def __start_display(self) -> None:
        """
        Display the hardware status.
        """
        with DisplayLock:
            t = threading.Thread(target=self.__display_loop, daemon=True)
            t.start()
        logger.info("Screen display started.")

    def __stop_display(self) -> None:
        """
        Turn off the screen.
        """
        with DisplayLock:
            self.__display = False
            if self.__lcd and self.__lcd.is_open():
                self.__lcd.close()
            if UIWindowManager.HWMonitorWindow:
                UIWindowManager.HWMonitorWindow.evaluate_js("window.flushDisplay(0)")
        logger.info("Screen display stopped.")


hardware_monitor_api = HardwareMonitorAPI()
