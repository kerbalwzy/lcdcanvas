from .VirtualScreen import LCD_VirtualScreen
from .SN_WCH32 import LCD_SN_WCH32
from .base import LCD, generate_random_image, image2rgb565_le

__all__ = [
    "LCD",
    "lcd_virtual_screen",
    "lcd_sn_wch32",
    "SUPPORT_SCREENS_MAP",
    "generate_random_image",
    "image2rgb565_le",
]

# Create lcd screen driver instances
lcd_virtual_screen = LCD_VirtualScreen()
lcd_sn_wch32 = LCD_SN_WCH32()

# Supported screen drivers map
SUPPORT_SCREENS_MAP = {
    lcd_sn_wch32.unique_id(): lcd_sn_wch32,
    lcd_virtual_screen.unique_id(): lcd_virtual_screen,
}
