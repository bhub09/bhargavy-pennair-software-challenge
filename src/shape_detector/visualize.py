import cv2
import numpy as np

from shape_detector.geometry import ShapeDetection3D
from .detector import ShapeDetection

OUTLINE_COLOR = (0, 0, 0) # Black
OUTLINE_THICKNESS = 2
CENTER_COLOR = (255, 255, 255) # White
CENTER_RADIUS = 3
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
FONT_THICKNESS = 1
CENTER_LABEL_COLOR = (0, 0, 0) # Black
COORD_LABEL_COLOR = (255, 255, 255) # White
LABEL_GAP = 5  # Gap between center point and label text


def draw_detections(image: np.ndarray, detections: list[ShapeDetection3D]) -> np.ndarray:
    annotated_image = image.copy()
    for detection in detections:
        # Reshape outline to OpenCV's format
        outline = detection["outline"].reshape(-1, 1, 2).astype(np.int32)  

        # Draw outline 
        cv2.drawContours(annotated_image, [outline], -1, OUTLINE_COLOR, OUTLINE_THICKNESS)

        # Draw center point
        cx, cy = int(detection["center"][0]), int(detection["center"][1])
        cv2.circle(annotated_image, (cx, cy), CENTER_RADIUS, CENTER_COLOR, -1)
        label = "center"
        (tw, th), _ = cv2.getTextSize(label, FONT, FONT_SCALE, FONT_THICKNESS)
        org = (cx - tw // 2, cy - CENTER_RADIUS - LABEL_GAP)
        cv2.putText(annotated_image, label, org, FONT, FONT_SCALE, CENTER_LABEL_COLOR, FONT_THICKNESS, cv2.LINE_AA)

        # Draw coordinates label
        bx, by, bw, bh = cv2.boundingRect(outline)          # outline in (N,1,2) form

        # Draw the coordinates label below the bounding box of the shape
        pos = detection.get("position")
        if pos is not None:
            px, py, pz = pos
            coords_text = f"({px:.1f}, {py:.1f}, {pz:.1f}) in"
        else:
            coords_text = "depth unavailable"
        coords_text = f"({px:.1f}, {py:.1f}, {pz:.1f}) in"


        cv2.putText(annotated_image, coords_text, (bx, by + bh + LABEL_GAP + 10),
            FONT, FONT_SCALE, COORD_LABEL_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    
    return annotated_image
        
    