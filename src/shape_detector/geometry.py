import math
import cv2
import numpy as np
from .detector import ShapeDetection


FX = 2564.3186869 # focal length for x
FY = 2569.70273111 # focal length for y
CIRCLE_RADIUS = 10.0 # in inches
REF_WIDTH = 1920.0  # resolution the intrinsic matrix was calibrated at
MIN_CIRCLENESS = 0.85   # minimum circleness for a shape to be considered a circle


class ShapeDetection3D(ShapeDetection):
    # X, Y, Z coordinates in inches, camera frame
    position: tuple[float, float, float]

def _touches_border(detection: ShapeDetection, frame_shape: tuple, margin: int = 2) -> bool:
    # check if the shape touches the border of the image frame
    h, w = frame_shape[:2]
    contour = detection["outline"].reshape(-1, 1, 2).astype(np.int32)
    bx, by, bw, bh = cv2.boundingRect(contour)
    return bx <= margin or by <= margin or bx + bw >= w - margin or by + bh >= h - margin

def find_reference_circle(detections: list[ShapeDetection], frame_shape: tuple) -> ShapeDetection | None:
    # find the most circular shape that does not touch the border of the image frame
    circles = [d for d in detections if circleness(d) >= MIN_CIRCLENESS and not _touches_border(d, frame_shape)]
    if not circles:
        return None
    best = max(circles, key=circleness)
    return best if circleness(best) >= MIN_CIRCLENESS else None

def _equivalent_radius(detection: ShapeDetection) -> float:
    # calculate the equivalent radius of a shape based on its area
    return math.sqrt(detection['area'] / math.pi)

def circleness(detection: ShapeDetection) -> float:
    # calculate the circleness of a shape based on its area and radius
    contour = detection["outline"].reshape(-1, 1, 2).astype(np.int32)
    (_, _), r = cv2.minEnclosingCircle(contour)
    if r == 0:
        return 0.0
    return detection["area"] / (math.pi * r * r)

def _scaled_focal(frame_shape: tuple) -> tuple[float, float]:
    # scale the focal lengths based on the current frame resolution
    scale = frame_shape[1] / REF_WIDTH
    return FX * scale, FY * scale

def calculate_depth(circle: ShapeDetection, frame_shape: tuple) -> float:
    # calculate the depth (Z coordinate) of the circle based on its equivalent and known radius
    fx, _ = _scaled_focal(frame_shape)
    return (CIRCLE_RADIUS * fx) / _equivalent_radius(circle)

def calculate_coords(detection: ShapeDetection, depth: float,
                        frame_shape: tuple) -> tuple[float, float, float]:
     
    fx, fy = _scaled_focal(frame_shape)
    h, w = frame_shape[:2]    # height and width of the image
    u = detection["center"][0] - w / 2      # principal point is (0,0), so
    v = detection["center"][1] - h / 2      # pixels are measured from center
    return (u * depth / fx, v * depth / fy, depth)
