"""RGB spatial resampling for new feedback experiments."""
import cv2

INTERPOLATION = cv2.INTER_LANCZOS4
BORDER_MODE = cv2.BORDER_REFLECT_101


def remap_rgb(rgb, coordinates):
    """Sample RGB at inverse coordinates using the selected Lanczos recipe."""
    return cv2.remap(rgb, coordinates, None, INTERPOLATION, borderMode=BORDER_MODE)
