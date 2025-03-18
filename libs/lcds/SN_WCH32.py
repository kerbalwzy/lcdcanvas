# AX206 USB VID:PID=1908:0102 SER=WCH32
import logging
import threading
import usb.core
import usb.util
from PIL import Image
from .base import LCD, image2rgb565_le


logger = logging.getLogger()


class LCD_SN_WCH32(LCD):

    VID = 0x1908
    PID = 0x0102
    SN = "WCH32"
    WIDTH = 480
    HEIGHT = 320

    def __init__(self):
        self.mutex = threading.Lock()
        self.device = None
        self.close()

    def __str__(self):
        return f"VID:PID={hex(self.VID)}:{hex(self.PID)} SER={self.SN}"

    def __del__(self):
        self.close()

    @classmethod
    def unique_id(cls) -> str:
        return cls.SN

    @classmethod
    def is_connected(cls) -> bool:
        try:
            device = usb.core.find(
                idVendor=cls.VID,
                idProduct=cls.PID,
            )
            if device is not None:
                try:
                    serial = device.serial_number
                    if serial:
                        return serial.replace("\x00", "") == cls.SN
                    return True
                except usb.core.USBError:
                    return True
            return False
        except Exception as e:
            return False

    def open(self):
        device = usb.core.find(
            idVendor=self.VID,
            idProduct=self.PID,
        )
        if device is not None:
            try:
                serial = device.serial_number
                if serial and serial.replace("\x00", "") == self.SN:
                    self.device = device
            except usb.core.USBError:
                self.device = device
        try:
            usb.util.dispose_resources(device)
        except Exception as e:
            pass

    def is_open(self) -> bool:
        return self.device is not None

    def close(self):
        if self.device is None:
            return
        if hasattr(self.device, "_ctx"):
            try:
                self.clear()
                self.device.reset()
            except Exception as e:
                pass
            try:
                usb.util.dispose_resources(self.device)
            except Exception as e:
                pass

        # 确保设备引用被清除
        self.device = None

    def write(self, data):
        with self.mutex:
            res = self.device.write(0x01, data, timeout=5000)
            if res == 0:
                raise ConnectionError("data write failed")

    def read(self, length):
        with self.mutex:
            return self.device.read(0x81, length)

    def handshake(self):
        handshake_data = bytearray(
            [
                0x55,
                0x53,
                0x42,
                0x43,
                0xDE,
                0xAD,
                0xBE,
                0xEF,
                0x05,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x10,
                0xCD,
                0x00,
                0x00,
                0x00,
                0x00,
                0x02,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )
        self.write(handshake_data)
        response = self.read(5)
        self.__do_ack()
        return response

    def display(self, img: Image.Image):
        img = img.resize((self.WIDTH, self.HEIGHT))
        width, height = img.size
        self.__init_display(0, 0, width, height)
        img_data = image2rgb565_le(img)
        self.write(bytearray(img_data))
        self.__do_ack()

    def clear(self):
        white_img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(255, 255, 255))
        self.display(white_img)

    def set_brightness(self, brightness):
        brightness = max(0, min(brightness, 100))
        mapped_brightness = int((brightness / 100) * 7)
        brightness_data = bytearray(
            [
                0x55,
                0x53,
                0x42,
                0x43,
                0xDE,
                0xAD,
                0xBE,
                0xEF,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x10,
                0xCD,
                0x00,
                0x00,
                0x00,
                0x00,
                0x06,
                0x01,
                0x01,
                0x00,
                mapped_brightness,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )
        self.write(brightness_data)
        self.__do_ack()

    def __do_ack(self):
        with self.mutex:
            return self.device.read(0x81, 13, timeout=1000)

    def __init_display(self, x0, y0, x1, y1):
        block_len = (x1 - x0) * (y1 - y0) * 2
        data = bytearray(
            [
                0x55,
                0x53,
                0x42,
                0x43,
                0xDE,
                0xAD,
                0xBE,
                0xEF,
                block_len & 0xFF,
                (block_len >> 8) & 0xFF,
                (block_len >> 16) & 0xFF,
                (block_len >> 24) & 0xFF,
                0x00,
                0x00,
                0x10,
                0xCD,
                0x00,
                0x00,
                0x00,
                0x00,
                0x06,
                0x12,
                x0 & 0xFF,
                (x0 >> 8) & 0xFF,
                y0 & 0xFF,
                (y0 >> 8) & 0xFF,
                (x1 - 1) & 0xFF,
                ((x1 - 1) >> 8) & 0xFF,
                (y1 - 1) & 0xFF,
                ((y1 - 1) >> 8) & 0xFF,
                0x00,
            ]
        )
        self.write(data)
