__all__ = ["t"]

from typing import List, Union
from app.setting import settings


class I18n:
    def __init__(self, loacle: str, fallbackLocale: str = None, messages: dict = None):
        self.locale = loacle
        self.fallbackLocale = fallbackLocale or loacle
        self.messages = messages or dict()
        assert (
            self.locale in self.messages
        ), f"I18n init error, locale<{loacle}> not in messages locales<{messages.keys()}>"
        assert (
            self.fallbackLocale in self.messages
        ), f"I18n init error, fallbackLocale<{self.fallbackLocale}> not in messages locales<{messages.keys()}>"

    def set_locale(self, locale: str):
        self.locale = locale

    def __find_result_in_message(
        self, locale: str, key_route: List[str]
    ) -> Union[str, None]:
        res = None
        message = self.messages.get(locale)
        for idx, k in enumerate(key_route):
            res = message.get(k, None)
            if idx == len(key_route) - 1:
                break
            if not (res and isinstance(res, dict)):
                res = None
                break
            message = res
        return res

    def t(self, key: str) -> str:
        assert isinstance(key, str)
        key_route = key.split(".")
        # find result in locale message
        res = self.__find_result_in_message(locale=self.locale, key_route=key_route)
        if res is None:
            # find result in fallbackLocale message
            res = self.__find_result_in_message(
                locale=self.fallbackLocale, key_route=key_route
            )
        if res is None:
            return key
        return res

    def __call__(self, key: str) -> str:
        return self.t(key)


t = I18n(
    loacle=settings.get_monitor_settings().get("lang", "zh"),
    fallbackLocale="en",
    messages={
        "zh": {
            "label": {
                "Quite": "退出",
                "Info": "信息",
                "Warning": "警告",
                "Error": "错误",
                "Yes": "是",
                "No": "否",
            },
            "msg": {
                "ThemeFileNotFound": "主题文件不存在",
                "ThemeFileImportSuccess": "主题文件导入成功",
                "ThemeFileDeleteSuccess": "主题文件删除成功",
                "FirstRunNeedAdmin": "首次运行请以管理员权限启动",
                "ThemeFileLoadFailed": "主题文件加载失败, 请选择有效的主题文件",
                "BrightnessSetFailed": "设置屏幕亮度失败, 请尝试重新连接屏幕",
                "ScreenDisplayFailed": "屏幕显示失败, 请尝试重新连接屏幕",
                "ThemeFileSameNameReplace": "相同名称的主题文件已存在, 你要替换它么?",
            },
        },
        "en": {
            "label": {
                "Quite": "Quite",
                "Info": "Info",
                "Warning": "Warning",
                "Error": "Error",
                "Yes": "Yes",
                "No": "No",
            },
            "msg": {
                "ThemeFileNotFound": "Theme file not found",
                "ThemeFileImportSuccess": "Theme file import success",
                "ThemeFileDeleteSuccess": "Theme file remove success",
                "FirstRunNeedAdmin": "Please start with administrator privileges for the first run",
                "ThemeFileLoadFailed": "Theme file load failed, please select a valid theme file",
                "BrightnessSetFailed": "Failed to set screen brightness, please try to reconnect the screen",
                "ScreenDisplayFailed": "Screen display failed, please try to reconnect the screen",
                "ThemeFileSameNameReplace": "A theme file with the same name already exists, do you want to replace it?",
            },
        },
    },
)
