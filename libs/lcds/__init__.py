from .SN_WCH32 import LCD_SN_WCH32
from .base import LCD, generate_random_image, image2rgb565_le

__all__ = [
    "LCD",
    "lcd_sn_qudtech",
    "lcd_sn_wch32",
    "SUPPORT_SCREENS_MAP",
    "generate_random_image",
    "image2rgb565_le",
]

lcd_sn_wch32 = LCD_SN_WCH32()

SUPPORT_SCREENS_MAP = {
    LCD_SN_WCH32.unique_id(): lcd_sn_wch32,
}
