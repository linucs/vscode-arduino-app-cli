from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger

logger: Incomplete

class Leds:
    """
    A utility class for controlling LED colors on Arduino hardware.

    This class provides static methods to control two RGB LEDs by writing to system
    brightness files. LED1 and LED2 can be controlled directly by the MPU, while
    LED3 and LED4 require MCU control via Bridge.

    Attributes:
        _led_ids (list): List of supported LED IDs [1, 2].
        _led1_brightness_files_legacy (list): Legacy file paths for LED1 brightness control.
        _led2_brightness_files_legacy (list): Legacy file paths for LED2 brightness control.
        _led1_brightness_file (list): Compatible file paths for LED1 brightness control.
        _led2_brightness_file (list): Compatible file paths for LED2 brightness control.

    Methods:
        set_led1_color(r, g, b): Set the RGB color state for LED1.
        set_led2_color(r, g, b): Set the RGB color state for LED2.

    Example:
        >>> Leds.set_led1_color(True, False, True)  # LED1 shows magenta
        >>> Leds.set_led2_color(False, True, False)  # LED2 shows green
    """
    @staticmethod
    def set_led1_color(r: bool, g: bool, b: bool): ...
    @staticmethod
    def set_led2_color(r: bool, g: bool, b: bool): ...
