import cv2
import numpy as np

def _local_mean(img: np.ndarray, k: int) -> np.ndarray:
    # Apply a local mean filter to the image
    return cv2.blur(img, (k, k))

def local_variance(gray: np.ndarray, k: int) -> np.ndarray:
    # Calculate the local variance of the grayscale image
    gray_f = gray.astype(np.float32)
    mean = _local_mean(gray_f, k)
    mean_sq = _local_mean(gray_f ** 2, k)
    variance = mean_sq - mean ** 2
    return variance