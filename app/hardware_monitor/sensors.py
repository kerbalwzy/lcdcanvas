"""
Hardware sensors, read hardware status data, implemented through the LibreHardwareMonitor dll library.

CPU:
    load: Utilization rate (%)
    frequency: Real-time frequency (GHz)
    temperature: Temperature (°C)
    fan: Fan speed (RPM)

GPU:
    load: Utilization rate (%)
    frequency: Real-time frequency (GHz)
    temperature: Temperature (°C)
    fan: Fan speed (RPM)
    total: Total video memory (GB)
    used: Used video memory (GB)

RAM:
    load: Utilization rate (%)
    used: Used memory (GB)
    free: Free memory (GB)
    total: Total memory (GB)

Disk:
    load: Utilization rate (%)
    used: Used storage (GB)
    free: Free storage (GB)
    total: Total capacity (GB)

Weather:
    text: Weather description
    icon: Weather icon

Net:
    speed (upload, download): Upload speed (B/s), Download speed (B/s)

Volume:
    load: Utilization rate (%)
"""

__all__ = ["cpu", "gpu", "ram", "disk", "net", "weather", "SensorsMap"]

import logging
import threading
import time
import requests
import clr  # type: ignore # Clr is from pythonnet package. Do not install clr package
import psutil

from statistics import mean
from typing import Union
from app.consts import LHM_LHMONITOR_DLL_PATH, LHM_HIDSHARP_DLL_PATH
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import POINTER, cast


# Import LibreHardwareMonitor dll to Python
clr.AddReference(LHM_LHMONITOR_DLL_PATH)
clr.AddReference(LHM_HIDSHARP_DLL_PATH)  # type: ignore, this dll is required by LibreHardwareMonitor.dll
from LibreHardwareMonitor import Hardware  # type: ignore

logger = logging.getLogger()

handle = Hardware.Computer()
handle.IsCpuEnabled = True
handle.IsGpuEnabled = True
handle.IsMemoryEnabled = True
handle.IsMotherboardEnabled = True  # For CPU Fan Speed
handle.IsControllerEnabled = True  # For CPU Fan Speed
handle.IsNetworkEnabled = True
handle.IsStorageEnabled = True
handle.IsPsuEnabled = False
handle.Open()

HARDWARE_TYPE_MOTHERBOARD = Hardware.HardwareType.Motherboard
HARDWARE_TYPE_CPU = Hardware.HardwareType.Cpu
HARDWARE_TYPE_MEN = Hardware.HardwareType.Memory
HARDWARE_TYPE_GPUNVIDIA = Hardware.HardwareType.GpuNvidia
HARDWARE_TYPE_GPUAMD = Hardware.HardwareType.GpuAmd
HARDWARE_TYPE_GPUINTEL = Hardware.HardwareType.GpuIntel
HARDWARE_TYPE_DISK = Hardware.HardwareType.Storage
HARDWARE_TYPE_NET = Hardware.HardwareType.Network


def print_hardware_and_status():
    for hardware in handle.Hardware:
        print(f"{hardware.HardwareType}: {hardware.Name}")
        hardware.Update()
        for sensor in hardware.Sensors:
            print(
                f"\t {sensor.SensorType}\t {sensor.Name} \t {round(sensor.Value, 2) if sensor.Value else ''}"
            )
        for sub_hardware in hardware.SubHardware:
            print(f"\t {sub_hardware.HardwareType}: {sub_hardware.Name}")
            sub_hardware.Update()
            for sensor in sub_hardware.Sensors:
                print(
                    f"\t\t {sensor.SensorType}\t {sensor.Name} \t {round(sensor.Value, 2) if sensor.Value else ''}"
                )


def get_hardware(filter, all: bool = False):
    """
    Get hardware devices based on the given filter condition. By default, only the first matching device is returned.

    :param filter: A callable object used to determine if a hardware device meets the condition.
    :param all: A boolean indicating whether to return all matching hardware devices.
    :return: The matching hardware device(s), or None if no device is found.
    """
    res = list()
    for hardware in handle.Hardware:
        if filter(hardware):
            if not all:
                return hardware
            else:
                res.append(hardware)
    return res


# CPU status data
class CPU:

    def __init__(self, hw: Hardware = None) -> None:
        if hw is None:
            hw = get_hardware(filter=lambda x: x.HardwareType == HARDWARE_TYPE_CPU)
        self.hw = hw
        self.load_sensor = None
        self.frequency_sensors = list()
        self.temperature_sensor = None
        self.fan_subhw = None
        self.fan_sensor = None

        tmp_temperature_sensors = dict()
        if self.hw is not None:
            self.hw.Update()
            for sensor in self.hw.Sensors:
                # Total CPU load
                if (
                    sensor.SensorType == Hardware.SensorType.Load
                    and sensor.Name.startswith("CPU Total")
                ):
                    self.load_sensor = sensor
                # CPU core frequency
                if (
                    sensor.SensorType == Hardware.SensorType.Clock
                    and "Core #" in sensor.Name
                    and "Effective" not in sensor.Name
                ):
                    self.frequency_sensors.append(sensor)
                # CPU temperature
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    tmp_temperature_sensors[sensor.Name] = sensor

        # CPU temperature
        for name, sensor in tmp_temperature_sensors.items():
            if name.startswith("Core Average"):
                self.temperature_sensor = sensor
                break
            if name.startswith("Core Max"):
                self.temperature_sensor = sensor
                break
            if name.startswith("CPU Package"):
                self.temperature_sensor = sensor
                break
            if name.startswith("Core"):
                self.temperature_sensor = sensor

        # CPU fan speed
        mb = get_hardware(filter=lambda x: x.HardwareType == HARDWARE_TYPE_MOTHERBOARD)
        if mb is not None:
            for subhw in mb.SubHardware:
                subhw.Update()  # Must update sub-hardware first
                for sensor in subhw.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Fan and "#2" in str(
                        sensor.Name
                    ):  # Is Motherboard #2 Fan always the CPU Fan?
                        self.fan_subhw = subhw
                        self.fan_sensor = sensor
                        break

    def update(self):
        self.hw is not None and self.hw.Update()
        self.fan_subhw is not None and self.fan_subhw.Update()

    def load(self) -> Union[float, None]:
        return self.load_sensor and max(round(self.load_sensor.Value / 100, 2), 0.01)

    def frequency(self) -> Union[float, None]:
        if self.frequency_sensors:
            res = mean([sensor.Value for sensor in self.frequency_sensors]) / 1000
            return round(res, 2)
        return None  # If no frequency sensor is found, return None

    def temperature(self) -> Union[int, None]:
        return self.temperature_sensor and int(self.temperature_sensor.Value)

    def fan(self) -> Union[int, None]:
        return self.fan_sensor and int(self.fan_sensor.Value)

    def status(self) -> dict:
        self.update()
        res = {
            "load": self.load(),
            "frequency": self.frequency(),
            "temperature": self.temperature(),
            "fan": self.fan(),
        }
        return res


# Always read the status data of the default first graphics card
class GPU:

    def __default_hw(self):
        # Prioritize using NVIDIA graphics cards
        hw = get_hardware(filter=lambda x: x.HardwareType == HARDWARE_TYPE_GPUNVIDIA)
        # If no NVIDIA graphics card is found, use an AMD graphics card
        if hw is None:
            hws = get_hardware(
                filter=lambda x: x.HardwareType == HARDWARE_TYPE_GPUAMD, all=True
            )
            # If there are AMD graphics cards, use the first one
            if len(hws) > 0:
                hw = hws[0]
            # When there are multiple AMD graphics cards, use the name to distinguish
            else:
                for tmp_hw in handle.Hardware:
                    for sensor in tmp_hw.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Load and str(
                            sensor.Name
                        ).startswith("GPU Core"):
                            hw = tmp_hw
                            break
                    if hw is not None:
                        break
        # If no AMD graphics card is found, use an Intel graphics card
        if hw is None:
            hw = get_hardware(filter=lambda x: x.HardwareType == HARDWARE_TYPE_GPUINTEL)
        return hw

    def __init__(self, hw: Hardware = None) -> None:
        if hw is None:
            hw = self.__default_hw()
        self.hw = hw
        self.load_sensor = None
        self.mem_controller_load_sensor = None
        self.frequency_sensor = None
        self.temperature_sensor = None
        self.fan_sensor = None
        self.mem_used_sensor = None
        self.mem_total = None

        if self.hw:
            self.hw.Update()  # When checking for values, must update once first
            for sensor in self.hw.Sensors:
                # GPU utilization
                if sensor.SensorType == Hardware.SensorType.Load:
                    if sensor.Name.startswith("GPU Core"):
                        self.load_sensor = sensor
                    elif sensor.Name.startswith("D3D 3D"):
                        self.load_sensor = self.load_sensor or sensor
                    if sensor.Name.startswith("GPU Memory Controller"):
                        self.mem_controller_load_sensor = sensor
                # GPU frequency
                if (
                    sensor.SensorType == Hardware.SensorType.Clock
                    and sensor.Name.startswith("GPU Core")
                    and "Effective" not in sensor.Name
                ):
                    self.frequency_sensor = sensor
                # GPU temperature
                if (
                    sensor.SensorType == Hardware.SensorType.Temperature
                    and sensor.Name.startswith("GPU Core")
                ):
                    self.temperature_sensor = sensor
                # GPU fan speed
                if (
                    sensor.SensorType == Hardware.SensorType.Fan
                    and sensor.Value is not None
                ):
                    self.fan_sensor = sensor
                # Video memory
                if sensor.SensorType == Hardware.SensorType.SmallData:
                    # Used video memory
                    if sensor.Name.startswith("GPU Memory Used"):
                        self.mem_used_sensor = sensor
                    if sensor.Name.startswith("D3D") and sensor.Name.endswith(
                        "Memory Used"
                    ):
                        self.mem_used_sensor = self.mem_used_sensor or sensor
                    # Total video memory
                    if sensor.Name.startswith("GPU Memory Total"):
                        self.mem_total = sensor.Value

    def update(self):
        self.hw and self.hw.Update()

    def load(self) -> Union[int, None]:
        # If the graphics card has a memory controller, subtract the memory controller's occupancy
        if self.load_sensor and self.mem_controller_load_sensor:
            res = self.load_sensor.Value + self.mem_controller_load_sensor.Value
            if res > 100:
                res = 100
            return round(res / 100, 2)

        return self.load_sensor and max(round(self.load_sensor.Value / 100, 2), 0.01)

    def frequency(self) -> Union[float, None]:
        return self.frequency_sensor and round(self.frequency_sensor.Value / 1000, 2)

    def temperature(self) -> Union[int, None]:
        return self.temperature_sensor and int(self.temperature_sensor.Value)

    def fan(self) -> Union[int, None]:
        return self.fan_sensor and int(self.fan_sensor.Value)

    def total(self) -> Union[float, None]:
        return self.mem_total and round(self.mem_total / 1024, 0)

    def used(self) -> Union[float, None]:
        return self.mem_used_sensor and round(self.mem_used_sensor.Value / 1024, 1)

    def free(self) -> Union[float, None]:
        if self.total() is None or self.used() is None:
            return None
        return self.total() - self.used()

    def status(self) -> dict:
        self.update()
        res = {
            "load": self.load(),
            "frequency": self.frequency(),
            "temperature": self.temperature(),
            "fan": self.fan(),
            "total": self.total(),
            "used": self.used(),
            "free": self.free(),
        }
        return res


# Disk status data (implemented based on psutil)
class Disk:

    def __init__(self) -> None:
        self.__last_update_at = None
        self.update()
    
    def update(self):
        # If the last update time is less than 60 seconds, do not update
        if self.__last_update_at and time.time() - self.__last_update_at < 60:
            return
        self._total = 0
        self._used = 0
        for part in psutil.disk_partitions():
            try:
                _usage = psutil.disk_usage(part.mountpoint)
                self._total += _usage.total
                self._used += _usage.used
            except Exception as e:
                logger.error(e)
                continue
        self._total = round(self._total / 1024 / 1024 / 1024, 0)  # GB
        self._used = round(self._used / 1024 / 1024 / 1024, 1)  # GB
        self._free = self._total - self._used
        self._load = round(self._used / self._total, 2)  # %
        self.__last_update_at = time.time()
        return self


    def status(self) -> dict:
        self.update()
        res = {
            "load": self._load,
            "used": self._used,
            "free": self._free,
            "total": self._total,
        }
        return res


# RAM status data (implemented based on psutil)
class RAM:
    def __init__(self) -> None:
        # Get the total memory directly during initialization
        self.__update()

    def __update(self):
        mem = psutil.virtual_memory()
        self.__total = mem.total
        self.__used = mem.used
        self.__available = mem.available
        self.__percent = mem.percent

    def update(self):
        """Keep compatible with the original interface"""
        self.__update()

    def load(self) -> float:
        """Return the load value between 0.00 and 1.00"""
        return round(self.__percent / 100, 2)

    def used(self) -> float:
        """Used memory (GB)"""
        return round(self.__used / (1024**3), 1)

    def free(self) -> float:
        """Available memory (GB)"""
        return round(self.__available / (1024**3), 1)

    def total(self) -> float:
        """Total memory (GB)"""
        return round(self.__total / (1024**3), 0)

    def status(self) -> dict:
        self.__update()
        res = {
            "load": self.load(),
            "used": self.used(),
            "free": self.free(),
            "total": self.total(),
        }
        return res


# Network status data (implemented based on psutil)
class Net:

    def __init__(self) -> None:
        self.last_update = time.time()
        self.time_diff = 0
        self.last_stats = psutil.net_io_counters(pernic=True)
        self.current_stats = self.last_stats.copy()
        self.virtual_interfaces = [
            "lo",
            "Loopback",
            "isatap",
            "Teredo",
            "VPN",
            "Virtual",
            "vEthernet",
            "VBox",
            "Hyper-V",
            "Docker",
        ]
        # Add valid value cache
        self.__last_valid_upload = 0
        self.__last_valid_download = 0

    def __filter_interface(self, name: str) -> bool:
        """Filter virtual network interfaces"""
        return not any(v.lower() in name.lower() for v in self.virtual_interfaces)

    def update(self):
        now = time.time()
        # Ensure minimum sampling interval (15ms)
        min_interval = 0.015
        elapsed = now - self.last_update
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
            now = time.time()

        self.time_diff = now - self.last_update
        self.last_stats = self.current_stats
        self.current_stats = psutil.net_io_counters(pernic=True)
        self.last_update = now

    def __calculate_speed(self, current, last, attr):
        valid_stats = []
        for iface in filter(self.__filter_interface, current):
            curr = getattr(current[iface], attr)
            prev = getattr(last[iface], attr)
            # Handle counter reset (32/64-bit overflow)
            diff = curr - prev if curr >= prev else curr
            valid_stats.append(diff)

        if not valid_stats or self.time_diff <= 0:
            return 0
        return sum(valid_stats) / self.time_diff

    def upload_speed(self) -> int:
        """Total upload speed (bytes/second)"""
        raw_speed = self.__calculate_speed(
            self.current_stats, self.last_stats, "bytes_sent"
        )
        # Data validation (filter out abnormal values)
        if 0 <= raw_speed <= 1e9:  # 1GB/s upper limit
            self.__last_valid_upload = int(raw_speed)
        return self.__last_valid_upload

    def download_speed(self) -> int:
        """Total download speed (bytes/second)"""
        raw_speed = self.__calculate_speed(
            self.current_stats, self.last_stats, "bytes_recv"
        )
        if 0 <= raw_speed <= 1e9:
            self.__last_valid_download = int(raw_speed)
        return self.__last_valid_download

    def status(self) -> dict:
        self.update()
        res = {
            "upload_speed": self.upload_speed(),
            "download_speed": self.download_speed(),
        }
        return res


# Weather data, obtained from openweathermap
# https://openweathermap.org/current
class Weather:

    def __init__(
        self,
        apiKey: str = "5796abbde9106b7da4febfae8c44c232",
        lat: float = 0,
        lon: float = 0,
    ) -> None:
        # Create a new Session and disable proxies
        self.session = requests.Session()
        self.session.trust_env = (
            False  # Disable proxy settings in environment variables
        )
        self.apiKey = apiKey
        self.lat = lat
        self.lon = lon
        self.__text = ""
        self.__icon = ""
        self.last_update = 0
        self.update_interval = (
            60 * 35
        )  # Update every 35 minutes when there is a cached value
        self.mutex = threading.Lock()  # Thread lock
        self.__update_async()

    def set_conf(self, apiKey: str, lat: float, lon: float):
        self.apiKey = apiKey
        self.lat = lat
        self.lon = lon
        self.__text = ""
        self.__icon = ""
        self.__update_async()

    def get_conf(self) -> dict:
        return {
            "apiKey": self.apiKey,
            "lat": self.lat,
            "lon": self.lon,
            "lang": self.lang,
        }

    def __cache_check(self):
        now = time.time()
        if (
            (now - self.last_update < self.update_interval)
            and self.__text
            and self.__icon
        ):
            return True
        return False

    def __update_async(self):
        # Cache check
        if self.__cache_check():
            return
        # Asynchronously update the weather
        thread = threading.Thread(target=self.__update, daemon=True)
        thread.start()

    def __update(self):
        # Thread-safe update of weather information
        with self.mutex:
            # Cache check again
            if self.__cache_check():
                return
            try:
                from app.i18n import t

                lang = t.locale  # https://openweathermap.org/current#multi
                if lang == "zh":
                    lang = "zh_cn"
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.apiKey}&lang={lang}&units=metric"
                res = self.session.get(url=url, timeout=1)
                data = res.json()
                self.__text = "%s\n%d°C" % (
                    data["weather"][0]["description"],
                    data["main"]["feels_like"],
                )
                self.__icon = data["weather"][0]["icon"]
                self.last_update = time.time()
            except requests.exceptions.Timeout:
                return
            except Exception as e:
                logger.error(e)
            else:
                logger.info(
                    f"Weather data updated successfully: text={self.__text} icon={self.__icon}"
                )

    def clean_cache(self):
        self.__text = ""
        self.__icon = ""
        self.last_update = 0

    def text(self) -> str:
        return self.__text

    def icon(self) -> str:
        return self.__icon

    def status(self) -> dict:
        self.__update_async()
        res = {
            "text": self.text(),
            "icon": self.icon(),
        }
        return res


# Volume
class Volume:
    def __init__(self) -> None:
        self.volume = None
        self.available = False
        try:
            CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            if devices:
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                if interface:
                    self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                    self.available = True
        except Exception as e:
            logger.warning(f"Audio device initialization failed: {e}")
            self.available = False

    def __del__(self):
        try:
            self.cleanup()
        except:
            pass

    def cleanup(self):
        if hasattr(self, "volume") and self.volume:
            self.volume.Release()
            self.volume = None
            CoUninitialize()

    def load(self) -> float:
        if not self.available or not self.volume:
            return 0.0  # Return 0 volume when no audio device is available
        try:
            current_volume = self.volume.GetMasterVolumeLevelScalar()
            return round(current_volume, 2)
        except Exception as e:
            logger.warning(f"Failed to get volume level: {e}")
            return 0.0

    def status(self) -> dict:
        res = {"load": self.load()}
        return res


# All sensors
cpu = CPU()
gpu = GPU()
ram = RAM()
disk = Disk()
net = Net()
weather = Weather()
volume = Volume()
SensorsMap = {
    "cpu": cpu,
    "gpu": gpu,
    "ram": ram,
    "disk": disk,
    "net": net,
    "weather": weather,
    "volume": volume,
}
