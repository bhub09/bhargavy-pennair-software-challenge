import cv2
import numpy as np
from .variance import local_variance
from typing import TypedDict


CLIP_PERCENTILE = 99
MIN_SOLIDITY = 0.7  
K_FRACTION = 0.01  # 1% of frame width/height
MIN_AREA_FRACTION = 0.005               # 0.5% of frame area

# Part 3 variables
VAR_FRACTION      = 0.004
SMOOTH_FRACTION   = 0.015




class ShapeDetection(TypedDict):
    center: tuple[float, float]
    outline: np.ndarray
    area: float

def _resolve_k(shape: tuple) -> int:
    return int(round(K_FRACTION * shape[1])) | 1

def _to_grayscale(image: np.ndarray) -> np.ndarray:
    # Convert color image to grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _build_shape_mask(gray: np.ndarray, k_small: int, k_large: int) -> np.ndarray:
    # Normalize variance map and apply Otsu thresholding separate shapes from the background
    raw_var = local_variance(gray, k_small)
    variance_map = cv2.blur(raw_var, (k_large, k_large))

    # let the bulk of the image set the scale, not outliers (apply log transform on variance map)
    log_var = np.log1p(variance_map)
    ceiling = np.percentile(log_var, CLIP_PERCENTILE)
    clipped = np.clip(log_var, 0, ceiling)

    normalized = cv2.normalize(clipped, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, mask = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # smooth boundary raggedness without changing region size
    smooth = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_small, k_small))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, smooth)

    recover = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_large, k_large))
    return cv2.dilate(mask, recover)

def _extract_contours(mask: np.ndarray) -> list[np.ndarray]:
    # Find contours in the binary mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def _contour_to_detection(contour: np.ndarray, min_area: float) -> ShapeDetection | None:
    # Convert contour to ShapeDetection object if it meets the area threshold (i.e. if it is large enough to be considered a shape)
    area = cv2.contourArea(contour)
    if area < min_area:
        return None

    hull_area = cv2.contourArea(cv2.convexHull(contour))

    # Minimum solidity (area / convex hull area) to consider a contour as a shape
    if hull_area == 0 or area / hull_area < MIN_SOLIDITY:
        return None
    
    M = cv2.moments(contour)

    if M["m00"] == 0:
        return None
    
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    outline = contour.reshape(-1, 2)    # Reshape contour to a 2D array of points
    detection = ShapeDetection(center=(cx, cy), outline=outline, area=area)
    return detection

def detect_shapes(
    image: np.ndarray,
    var_fraction: float = VAR_FRACTION,
    smooth_fraction: float = SMOOTH_FRACTION,
    min_area_fraction: float = MIN_AREA_FRACTION,
) -> list[ShapeDetection]:
    # Detect shapes in the input image and return a list of ShapeDetection objects
    gray = _to_grayscale(image)
    h, w = image.shape[:2]
    k_small = int(round(var_fraction * w)) | 1
    k_large = int(round(smooth_fraction * w)) | 1
    min_area = min_area_fraction * h * w

    mask = _build_shape_mask(gray, k_small, k_large)
    contours = _extract_contours(mask)
    detections = [_contour_to_detection(c, min_area) for c in contours]
    return [d for d in detections if d is not None]

