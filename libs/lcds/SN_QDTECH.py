# coding: utf-8
# For LCD SER = "QDTECH", size = 320x480
import threading
import logging
import time
import numpy as np
import serial.tools.list_ports
from PIL import Image
from ._base import LCD, image2rgb565_le


logger = logging.getLogger()


class LCD_SN_QDTECH(LCD):

    BYTES_PER_PIXEL = 2
    SN = "QDTFT35_V1COM"
    width = 320
    height = 480

    def __init__(self):
        self.mutex = threading.Lock()
        self.port = None
        self.last_img_data = None

    @classmethod
    def unique_id(cls) -> str:
        return cls.SN

    @classmethod
    def is_connected(cls) -> bool:
        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.serial_number == cls.SN:
                    return True
        except Exception as e:
            logger.error(e)
        return False

    def open(self):
        ports = serial.tools.list_ports.comports()
        try:
            for port in ports:
                if port.serial_number == self.SN:
                    self.port = serial.Serial(port.device, baudrate=115200, timeout=1)
                    self.port.reset_input_buffer()
                    self.port.reset_output_buffer()
                    break
        except Exception as e:
            logger.error(e)
            self.port = None

    def is_open(self) -> bool:
        if self.port:
            return self.port.is_open
        return False

    def close(self):
        if self.port:
            try:
                self.clear()
                self.port.close()
            except Exception as e:
                logger.error(e)
            self.port = None
        self.last_img_data = None

    def write(self, buf):
        if not self.is_open():
            raise Exception("Serial port is not open")

        with self.mutex:
            self.port.write(buf)
            self.port.flush()

    def read(self, length):
        with self.mutex:
            if not self.port.is_open:
                self.__open()
            return self.port.read(length)

    def handshake(self):
        dat = 3
        command = self.__create_command(cmd=200, data=dat)
        self.write(command)
        response = self.read(16)
        if dat == 3:
            device_unique_id = response.hex().upper().strip()
            logger.debug(f"Handshake ok, device unique id:: {device_unique_id}")
        if dat == 4:
            logger.debug(f"Handshake ok, device info: {response.decode()}")
        return response

    def display(self, img: Image.Image):
        # resize image to 320x480 if needed
        if img.size != (self.width, self.height):
            img = img.resize((self.width, self.height))
        # convert image to RGB565
        current_img_data = image2rgb565_le(img)
        width, height = img.size
        # compare with last frame data
        update_rect = self.__calculate_diff_region(current_img_data, width, height)
        if update_rect:
            (x1, x2, y1, y2) = update_rect
            command = self.__create_command(
                cmd=197,
                x_start=x1,
                x_end=x2 - 1,  
                y_start=y1,
                y_end=y2 - 1  
            )
            diff_data = self.__get_region_data(current_img_data, width, x1, x2, y1, y2)
            self.write(command)
            self.write(diff_data)
            logger.debug(
                f"Flush area: {x1}-{x2} x {y1}-{y2}, data: {len(diff_data)//1024}KB"
            )
        else:
            logger.debug("No update, skip flush")
        self.last_img_data = current_img_data

    def clear(self):
        command = self.__create_command(cmd=102, data=0xFF, x_start=0xFFFF)
        self.write(command)
        self.last_img_data = None
        logger.debug("clear ok")

    def set_brightness(self, brightness):
        brightness = max(0, min(brightness, 100))
        mapped_brightness = int((brightness / 100) * 255)
        command = self.__create_command(cmd=110, data=mapped_brightness)
        self.write(command)
        logger.debug("set_brightness ok")

    def __create_command(self, cmd, data=0, x_start=0, x_end=0, y_start=0, y_end=0):
        command = [
            (x_start >> 8) & 0xFF,  # XStart-H
            x_start & 0xFF,  # XStart-L
            (x_end >> 8) & 0xFF,  # XEnd-H
            x_end & 0xFF,  # XEnd-L
            (y_start >> 8) & 0xFF,  # YStart-H
            y_start & 0xFF,  # YStart-L
            (y_end >> 8) & 0xFF,  # YEnd-H
            y_end & 0xFF,  # YEnd-L
            cmd & 0xFF,  # Command
            data & 0xFF,  # Data
        ]
        logger.debug(f"Command: {command}")
        return bytes(command)

    def __calculate_diff_region(self, current_data, width, height):
        if self.last_img_data is None:
            return (0, width, 0, height)
        if len(self.last_img_data) != len(current_data):
            logger.warning("Frame size mismatch, full refresh")
            return (0, width, 0, height)

        current_arr = np.frombuffer(current_data, dtype=np.uint16)
        last_arr = np.frombuffer(self.last_img_data, dtype=np.uint16)
        diff_mask = current_arr != last_arr

        if not np.any(diff_mask):
            return None

        y_indices, x_indices = np.where(diff_mask.reshape(height, width))
        min_x, max_x = np.min(x_indices), np.max(x_indices)
        min_y, max_y = np.min(y_indices), np.max(y_indices)

        # Modified region calculation to ensure complete coverage of differences
        min_x = max(0, (min_x // 8) * 8)  # Align to 8 pixels
        max_x = min(width, ((max_x + 7) // 8) * 8)  # Round up to 8-pixel blocks
        
        # Ensure sufficient safety margin in Y direction
        min_y = max(0, min_y - 2)
        max_y = min(height, max_y + 2)
        
        return (min_x, max_x, min_y, max_y)

    def __get_region_data(self, data, width, x1, x2, y1, y2):
        bytes_per_row = width * self.BYTES_PER_PIXEL
        region_width = x2 - x1
    
        required_bytes = region_width * self.BYTES_PER_PIXEL
        region_data = bytearray(required_bytes * (y2 - y1))
        
        for y in range(y1, y2):
            row_start = y * bytes_per_row + x1 * self.BYTES_PER_PIXEL
            row_end = row_start + required_bytes
            region_data[(y-y1)*required_bytes:(y-y1+1)*required_bytes] = \
                data[row_start:row_end]
        
        return bytes(region_data)
