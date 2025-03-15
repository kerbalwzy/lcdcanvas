from PIL import Image
import numpy as np
from random import randint

# lcd interface base clase
class LCD:

    @classmethod
    def unique_id(cls) -> str:
        raise NotImplementedError

    @classmethod
    def is_connected(cls) -> bool:
        raise NotImplementedError

    def open(self) -> None:
        raise NotImplementedError
    
    def is_open(self) -> bool:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def close(self):
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def write(self, data: bytes) -> None:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def read(self, length: int) -> bytes:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def handshake(self) -> None:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def display(self, image: Image.Image) -> None:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def clear(self) -> None:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def set_brightness(self, brightness: int) -> None:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

    def __str__(self) -> str:
        # Raise an error indicating that the method is not implemented
        raise NotImplementedError

# Convert the image to RGB565LE format
def image2rgb565_le(image: Image.Image):
    if image.mode != "RGB":
        image = image.convert("RGB")
    # Use more precise bitwise operations
    rgb = np.asarray(image, dtype=np.uint32)  # Increase precision to avoid overflow
    r = (rgb[..., 0] >> 3).astype(np.uint16)  # 5-bit red
    g = (rgb[..., 1] >> 2).astype(np.uint16)  # 6-bit green
    b = (rgb[..., 2] >> 3).astype(np.uint16)  # 5-bit blue
    # Correct the bit combination order
    rgb565 = (r << 11) | (g << 5) | b
    # Restore the original byte order processing method
    return rgb565.byteswap().tobytes()

# Generate a random image
def generate_random_image(width: int, height: int):
    # Create random pixel data
    pixels = [
        (randint(0, 255), randint(0, 255), randint(0, 255))
        for _ in range(width * height)
    ]
    # Create an image
    random_img = Image.new("RGB", (width, height))
    random_img.putdata(pixels)
    return random_img
