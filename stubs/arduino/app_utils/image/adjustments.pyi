import numpy as np
from PIL import Image
from arduino.app_utils.image.pipeable import PipeableFunction as PipeableFunction

def letterbox(frame: np.ndarray, target_size: tuple[int, int] | None = None, color: tuple[int, int, int] | tuple[int, int, int, int] = (114, 114, 114), interpolation: int = ...) -> np.ndarray:
    """
    Add letterboxing to frame to achieve target size while maintaining aspect ratio.

    Args:
        frame (np.ndarray): Input frame
        target_size (tuple, optional): Target size as (width, height). If None, makes frame square.
        color (tuple): BGR or BGRA color for padding borders. Default: (114, 114, 114)
        interpolation (int, optional): OpenCV interpolation method. Default: cv2.INTER_LINEAR

    Returns:
        np.ndarray: Letterboxed frame
    """
def resize(frame: np.ndarray, target_size: tuple[int, int], maintain_ratio: bool = False, interpolation: int = ...) -> np.ndarray:
    """
    Resize frame to target size.

    Args:
        frame (np.ndarray): Input frame
        target_size (tuple): Target size as (width, height)
        maintain_ratio (bool): If True, use letterboxing to maintain aspect ratio. Default: False.
        interpolation (int): OpenCV interpolation method. Default: cv2.INTER_LINEAR.

    Returns:
        np.ndarray: Resized frame
    """
def flip_h(frame: np.ndarray) -> np.ndarray:
    """
    Flip frame horizontally.

    Args:
        frame (np.ndarray): Input frame

    Returns:
        np.ndarray: Horizontally flipped frame
    """
def flip_v(frame: np.ndarray) -> np.ndarray:
    """
    Flip frame vertically.

    Args:
        frame (np.ndarray): Input frame

    Returns:
        np.ndarray: Vertically flipped frame
    """
def crop(frame: np.ndarray, width: int, height: int, x: int | None = None, y: int | None = None) -> np.ndarray:
    """
    Crop frame to specified region. If x and y are not provided, the crop is centered.

    Args:
        frame (np.ndarray): Input frame
        width (int): Width of crop region
        height (int): Height of crop region
        x (int, optional): Left coordinate of crop region. If None, centers horizontally.
            Default: None.
        y (int, optional): Top coordinate of crop region. If None, centers vertically.
            Default: None.

    Returns:
        np.ndarray: Cropped frame
    """
def crop_to_aspect_ratio(frame: np.ndarray, aspect_ratio: tuple[int, int], x: int | None = None, y: int | None = None) -> np.ndarray:
    """
    Crop frame to specified aspect ratio. If x and y are not provided, the crop is
    centered. The function will crop the minimum amount necessary to achieve the
    target aspect ratio.

    Args:
        frame (np.ndarray): Input frame
        aspect_ratio (tuple): Target aspect ratio as tuple (e.g., (16, 9), (1, 1))
        x (int, optional): Left coordinate of crop region. If None, centers horizontally.
            Default: None.
        y (int, optional): Top coordinate of crop region. If None, centers vertically.
            Default: None.

    Returns:
        np.ndarray: Cropped frame with target aspect ratio

    Examples:
        crop_to_aspect_ratio(frame, (16, 9))  # Crop to 16:9 aspect ratio
        crop_to_aspect_ratio(frame, (4, 3))  # Crop to 4:3 aspect ratio
        crop_to_aspect_ratio(frame, (1, 1))  # Crop to square
    """
def rotate(frame: np.ndarray, angle: float, center: tuple[int, int] | None = None, expand: bool = False, color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 0), interpolation: int = ...) -> np.ndarray:
    """
    Rotate frame by specified angle.

    Args:
        frame (np.ndarray): Input frame
        angle (float): Rotation angle in degrees (positive values rotate counter-clockwise)
        center (tuple, optional): Center of rotation as (x, y). If None, uses image center.
            Default: None.
        expand (bool): If True, expands the output frame to fit the entire rotated image.
            If False, output frame size matches input. Default: False.
        color (tuple): BGR or BGRA color for border pixels. Default: (0, 0, 0).
        interpolation (int): OpenCV interpolation method. Default: cv2.INTER_LINEAR.

    Returns:
        np.ndarray: Rotated frame

    Examples:
        rotate(frame, 45)  # Rotate 45 degrees counter-clockwise
        rotate(frame, -90)  # Rotate 90 degrees clockwise
        rotate(frame, 30, expand=True)  # Rotate 30 degrees and expand to fit
    """
def adjust(frame: np.ndarray, brightness: float = 0.0, contrast: float = 1.0, saturation: float = 1.0, gamma: float = 1.0) -> np.ndarray:
    """
    Apply image adjustments to a BGR or BGRA frame, preserving channel count
    and data type.

    Args:
        frame (np.ndarray): Input frame (uint8, uint16, uint32).
        brightness (float): -1.0 to 1.0. Default: 0.0.
        contrast (float): 0.0 to N. Default: 1.0.
        saturation (float): 0.0 to N. Default: 1.0.
        gamma (float): > 0. Default: 1.0.

    Returns:
        np.ndarray: The adjusted input with same dtype as frame.
    """
def split_channels(frame: np.ndarray) -> tuple:
    """
    Split a multi-channel frame into individual channels using numpy indexing.
    This function provides better data type compatibility than cv2.split,
    especially for uint32 data which OpenCV doesn't fully support.

    Args:
        frame (np.ndarray): Input frame with 3 or 4 channels

    Returns:
        tuple: Individual channel arrays. For BGR: (b, g, r). For BGRA: (b, g, r, a).
               For HSV: (h, s, v). For other 3-channel: (ch0, ch1, ch2).
    """
def greyscale(frame: np.ndarray) -> np.ndarray:
    """
    Converts a BGR or BGRA frame to greyscale, preserving channel count and
    data type. A greyscale frame is returned unmodified.

    Args:
        frame (np.ndarray): Input frame (uint8, uint16, uint32).

    Returns:
        np.ndarray: The greyscaled frame with same dtype and channel count as frame.
    """
def compress_to_jpeg(frame: np.ndarray, quality: int = 80) -> np.ndarray | None:
    """
    Compress frame to JPEG format.

    Args:
        frame (np.ndarray): Input frame as numpy array
        quality (int): JPEG quality (0-100, higher = better quality)

    Returns:
        bytes: Compressed JPEG data, or None if compression failed
    """
def compress_to_png(frame: np.ndarray, compression_level: int = 6) -> np.ndarray | None:
    """
    Compress frame to PNG format.

    Args:
        frame (np.ndarray): Input frame as numpy array
        compression_level (int): PNG compression level (0-9, higher = better compression)

    Returns:
        bytes: Compressed PNG data, or None if compression failed
    """
def numpy_to_pil(frame: np.ndarray) -> Image.Image:
    """
    Convert numpy array to PIL Image.

    Args:
        frame (np.ndarray): Input frame in BGR format

    Returns:
        PIL.Image.Image: PIL Image in RGB format
    """
def pil_to_numpy(image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to numpy array.

    Args:
        image (PIL.Image.Image): PIL Image

    Returns:
        np.ndarray: Numpy array in BGR format
    """
def letterboxed(target_size: tuple[int, int] | None = None, color: tuple[int, int, int] | tuple[int, int, int, int] = (114, 114, 114), interpolation: int = ...):
    """
    Pipeable letterbox function - apply letterboxing with pipe operator support.

    Args:
        target_size (tuple, optional): Target size as (width, height). If None, makes frame square.
        color (tuple): BGR or BGRA color for padding borders. Default: (114, 114, 114)
        interpolation (int): OpenCV interpolation method. Default: cv2.INTER_LINEAR

    Returns:
        Function that takes a frame and returns letterboxed frame

    Examples:
        pipe = letterboxed(target_size=(640, 640))
        pipe = letterboxed() | greyscaled()
    """
def resized(target_size: tuple[int, int], maintain_ratio: bool = False, interpolation: int = ...):
    """
    Pipeable resize function - resize frame with pipe operator support.

    Args:
        target_size (tuple): Target size as (width, height)
        maintain_ratio (bool): If True, use letterboxing to maintain aspect ratio
        interpolation (int): OpenCV interpolation method. Default: cv2.INTER_LINEAR

    Returns:
        Function that takes a frame and returns resized frame

    Examples:
        pipe = resized(target_size=(640, 480))
        pipe = letterboxed() | resized(target_size=(320, 240))
    """
def flipped_h():
    """
    Pipeable horizontal flip function - flip frame horizontally with pipe operator support.

    Returns:
        Function that takes a frame and returns horizontally flipped frame
    """
def flipped_v():
    """
    Pipeable vertical flip function - flip frame vertically with pipe operator support.

    Returns:
        Function that takes a frame and returns vertically flipped frame
    """
def cropped(width: int, height: int, x: int | None = None, y: int | None = None):
    """
    Pipeable crop function - crop frame with pipe operator support.
    If x and y are not provided, the crop is centered.

    Args:
        width (int): Width of crop region
        height (int): Height of crop region
        x (int, optional): Left coordinate of crop region. If None, centers
            horizontally. Default: None.
        y (int, optional): Top coordinate of crop region. If None, centers
            vertically. Default: None.

    Returns:
        Function that takes a frame and returns cropped frame

    Examples:
        pipe = cropped(width=400, height=300)  # Centered crop
        pipe = cropped(width=400, height=300, x=100, y=100)
        pipe = letterboxed() | cropped(width=640, height=480)
    """
def cropped_to_aspect_ratio(aspect_ratio: tuple[int, int], x: int | None = None, y: int | None = None):
    """
    Pipeable crop to aspect ratio function - crop frame to aspect ratio with
    pipe operator support.
    If x and y are not provided, the crop is centered.

    Args:
        aspect_ratio (tuple): Target aspect ratio as tuple (e.g., (16, 9), (4, 3), (1, 1))
        x (int, optional): Left coordinate of crop region. If None, centers horizontally.
            Default: None.
        y (int, optional): Top coordinate of crop region. If None, centers vertically.
            Default: None.

    Returns:
        Function that takes a frame and returns cropped frame with target aspect ratio

    Examples:
        pipe = cropped_to_aspect_ratio((16, 9))  # Crop to 16:9 aspect ratio
        pipe = cropped_to_aspect_ratio((4, 3))  # Crop to 4:3 aspect ratio
        pipe = letterboxed() | cropped_to_aspect_ratio((1, 1))  # Square crop
    """
def rotated(angle: float, center: tuple[int, int] | None = None, expand: bool = False, color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 0), interpolation: int = ...):
    """
    Pipeable rotate function - rotate frame with pipe operator support.
    If center is not provided, rotates around the image center.

    Args:
        angle (float): Rotation angle in degrees (positive values rotate counter-clockwise)
        center (tuple, optional): Center of rotation as (x, y). If None, uses image center.
            Default: None.
        expand (bool): If True, expands the output frame to fit the entire rotated image.
            If False, output frame size matches input. Default: False.
        color (tuple): BGR or BGRA color for border pixels. Default: (0, 0, 0).
        interpolation (int): OpenCV interpolation method. Default: cv2.INTER_LINEAR.

    Returns:
        Function that takes a frame and returns rotated frame

    Examples:
        pipe = rotated(45)  # Rotate 45 degrees counter-clockwise
        pipe = rotated(-90)  # Rotate 90 degrees clockwise
        pipe = letterboxed() | rotated(30, expand=True)
    """
def adjusted(brightness: float = 0.0, contrast: float = 1.0, saturation: float = 1.0, gamma: float = 1.0):
    """
    Pipeable adjust function - apply image adjustments with pipe operator support.

    Args:
        brightness (float): -1.0 to 1.0. Default: 0.0.
        contrast (float): 0.0 to N. Default: 1.0.
        saturation (float): 0.0 to N. Default: 1.0.
        gamma (float): > 0. Default: 1.0.

    Returns:
        Function that takes a frame and returns adjusted frame

    Examples:
        pipe = adjusted(brightness=0.1, contrast=1.2)
        pipe = letterboxed() | adjusted(saturation=0.8)
    """
def greyscaled():
    """
    Pipeable greyscale function - convert frame to greyscale with pipe operator support.

    Returns:
        Function that takes a frame and returns greyscale frame

    Examples:
        pipe = greyscaled()
        pipe = letterboxed() | greyscaled()
    """
def compressed_to_jpeg(quality: int = 80):
    """
    Pipeable JPEG compression function - compress frame to JPEG with pipe operator support.

    Args:
        quality (int): JPEG quality (0-100, higher = better quality)

    Returns:
        Function that takes a frame and returns compressed JPEG bytes as Numpy array or None

    Examples:
        pipe = compressed_to_jpeg(quality=95)
        pipe = resized(target_size=(640, 480)) | compressed_to_jpeg()
    """
def compressed_to_png(compression_level: int = 6):
    """
    Pipeable PNG compression function - compress frame to PNG with pipe operator support.

    Args:
        compression_level (int): PNG compression level (0-9, higher = better compression)

    Returns:
        Function that takes a frame and returns compressed PNG bytes as Numpy array or None

    Examples:
        pipe = compressed_to_png(compression_level=9)
        pipe = letterboxed() | compressed_to_png()
    """
