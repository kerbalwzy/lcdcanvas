import logging
import os
from typing import List
from app import consts
from app.hardware_monitor.sensors import SensorsMap
from app.ui import UIAPIBase

__all__ = ["theme_player_api"]
logger = logging.getLogger()


class ThemePlayerAPI(UIAPIBase):

    def loadTheme(self, theme: str = None) -> str:
        """
        Load the theme content.
        Args:
            theme (str): The name of the theme to load.
        Returns:
            str: The content of the theme file, or an empty string if the theme is not set.
        """
        content: str = ""
        if not theme:
            return content
        # Construct the theme file path
        filepath: str = os.path.join(consts.THEMES_DIR, f"{theme}.json")
        with open(filepath, "r", encoding="utf-8") as fp:
            content: str = fp.read()
        logger.debug(f"Theme player selected theme <{theme}>")
        return content

    def loadSensorsValue(self, sensors: List[str]) -> dict:
        """
        Get sensor data.

        Args:
            sensors (List[str]): List of sensor names.

        Returns:
            dict: A dictionary containing sensor names and their corresponding status.
        """
        if not sensors:
            return dict()
        res = dict()
        for sensor in sensors:
            # Get the sensor instance from the SensorsMap
            instance = SensorsMap.get(sensor, None)
            if instance:
                res[sensor] = instance.status()
        # logger.debug(f"Theme player loaded sensor <{sensors}> data: {res}")
        return res


theme_player_api = ThemePlayerAPI()
