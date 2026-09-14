import cv2
from shape_detector.detector import detect_shapes
from shape_detector.detector import _to_grayscale, _build_shape_mask


img = cv2.imread("media/input/pennair_static_image.png")  # adjust to your actual file path
detections = detect_shapes(img)

gray = _to_grayscale(img)
mask = _build_shape_mask(gray)
cv2.imwrite("debug_mask.png", mask)


print(f"Found {len(detections)} shapes")
for d in detections:
    print(d["center"], d["area"])