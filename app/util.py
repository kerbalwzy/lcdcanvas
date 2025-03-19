# coding:utf-8
import base64
import ctypes
from io import BytesIO
import logging
import os
import platform
import shutil
from PIL import Image, ImageFile
import psutil
import sys
import subprocess
from .consts import IS_EXE, THEMES_SOURCE_DIR, THEMES_DIR
from .i18n import t
from .ui import UIAPIBase


logger = logging.getLogger()


def set_always_runas_admin():
    """
    Set the program to always run as an administrator on Windows.
    """
    if platform.system() == "Windows":
        import winreg as reg

        # Get the program name
        executable = os.path.abspath(sys.argv[0])
        # Registry path
        reg_path = (
            r"Software\\Microsoft\Windows NT\\CurrentVersion\AppCompatFlags\\Layers"
        )
        try:
            # Open the registry path
            reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, reg_path, 0, reg.KEY_SET_VALUE)
            # Set the registry value of the program to mark it as running with administrator privileges
            reg.SetValueEx(reg_key, executable, 0, reg.REG_SZ, "~ RUNASADMIN")
            # Close the registry
            reg.CloseKey(reg_key)

            logger.info(f"Successfully set always run as administrator.")
        except Exception as e:
            logger.error(f"Failed to set always run as administrator, error: {e}")


def is_runas_admin():
    """
    Check if the current process is running as an administrator.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def require_runas_admin():
    """
    The program must be started as an administrator.
    """
    if not IS_EXE:
        return
    if not is_runas_admin():
        # If it is a compiled executable, modify the registry to always run as an administrator
        set_always_runas_admin()
        # Show a pop-up window to prompt the user to restart with administrator privileges
        UIAPIBase.showwarning(t("msg.FirstRunNeedAdmin"))
        try:
            sys.exit(0)
        except:
            os._exit(0)


def require_runas_unique():
    """
    The program must be started as a unique process.
    """
    if not IS_EXE:
        return
    # Kill processes with the same name before starting
    current_pid = os.getpid()
    current_ppid = os.getppid()
    executable = os.path.abspath(sys.argv[0])
    program_name = os.path.basename(executable)
    for proc in psutil.process_iter(["pid", "name"]):
        pid = proc.info["pid"]
        if (
            proc.info["name"] == program_name
            and pid != current_ppid
            and pid != current_pid
        ):
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait()  
            except Exception:
                pass
            else:
                logger.warning(f"Killed same name process with PID: {pid}")


def image_from_base64(base64_str: str) -> ImageFile.ImageFile:
    """
    Convert a base64 string to an image.
    """
    # Remove the prefix from the Base64 string (e.g., "data:image/png;base64,")
    base64_string = base64_str.split("base64,", 1)[1]
    # Decode the binary data from the Base64 string
    image_data = base64.b64decode(base64_string)
    # Create a BytesIO object to convert the binary data to an image
    image_stream = BytesIO(image_data)
    return Image.open(image_stream)


def image_to_base64(image: ImageFile.ImageFile) -> str:
    """
    Convert an image to a base64 string.
    """
    # Create a BytesIO object to store the converted binary data
    image_stream = BytesIO()
    # Save the image to the BytesIO object
    image.save(image_stream, format="PNG")
    # Get the binary data
    image_data = image_stream.getvalue()
    # Encode the binary data to a Base64 string
    base64_string = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/png;base64,{base64_string}"


def set_win_startup(name: str, exepath: str):
    """
    Set the program to start up automatically on Windows.
    """
    # Define the command and parameters
    del_command = ["schtasks", "/delete", "/tn", name, "/f"]
    set_command = [
        "schtasks",
        "/create",
        "/tn",
        name,
        "/tr",
        exepath,
        "/sc",
        "onlogon",
        "/ru",
        os.getlogin(),
        "/rl",
        "highest",
    ]

    # Execute the command
    try:
        subprocess.run(
            del_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        result = subprocess.run(
            set_command, check=True, text=True, capture_output=True, timeout=2
        )
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)


def del_win_startup(name: str):
    """
    Delete the Windows startup entry.
    """
    # Define the command and parameters
    command = ["schtasks", "/delete", "/tn", name, "/f"]
    # Execute the command
    try:
        result = subprocess.run(
            command, check=True, text=True, capture_output=True, timeout=2
        )
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)


def copy_theme_to_user_dir():
    """
    Copy the theme to the user directory.
    """
    # Define the source directory and the target directory
    source_dir = THEMES_SOURCE_DIR
    target_dir = THEMES_DIR
    # Check if the source directory exists
    if not os.path.exists(source_dir):
        logger.error(
            f"The source directory {source_dir} does not exist and cannot be copied."
        )
        return
    # Check if the target directory exists, and create it if it does not
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Traverse all files and folders in the source directory
    for root, dirs, files in os.walk(source_dir):
        # Calculate the corresponding path of the current source directory in the target directory
        relative_path = os.path.relpath(root, source_dir)
        target_sub_dir = os.path.join(target_dir, relative_path)
        # Create the target subdirectory if it does not exist
        if not os.path.exists(target_sub_dir):
            os.makedirs(target_sub_dir)
        # Copy files
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_sub_dir, file)
            # Check if the target file already exists, and copy it if it does not
            if not os.path.exists(target_file):
                shutil.copy2(source_file, target_file)
                logger.debug(f"Copied file: {source_file} to {target_file}")
            else:
                logger.debug(f"Skipped existing file: {target_file}")
