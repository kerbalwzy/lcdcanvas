from typing import Dict
from ._base import LCD, generate_random_image, image2rgb565_le
from .VirtualScreen import LCD_VirtualScreen
from .SecondScreen import find_2nd_screen

__all__ = [
    "LCD",
    "lcd_virtual_screen",
    "SUPPORT_SCREENS_MAP",
    "generate_random_image",
    "image2rgb565_le",
]

# Create lcd screen driver instances
lcd_virtual_screen = LCD_VirtualScreen()


# Supported and connected screens map
def find_connected_screens() -> Dict[str, LCD]:
    """Find all supported screen"""
    res = {
        lcd_virtual_screen.unique_id(): lcd_virtual_screen,
    }
    #
    for screen in find_2nd_screen():
        res[screen.unique_id()] = screen
    #
    if lcd_virtual_screen.is_connected():
        res[lcd_virtual_screen.unique_id()] = lcd_virtual_screen
    return res
