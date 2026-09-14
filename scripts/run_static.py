import cv2
import numpy as np
import argparse
from shape_detector.detector import detect_shapes, ShapeDetection
from shape_detector.visualize import draw_detections
from pathlib import Path
from shape_detector.geometry import calculate_depth, calculate_coords, circleness


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "media" / "input"
OUTPUT_DIR = PROJECT_ROOT / "media" / "output"

def main():
    parser = argparse.ArgumentParser(description="Detect shapes in an image and save the annotated output.")
    parser.add_argument("image", type=str, help="Filename of an image in media/input/")
    parser.add_argument("--var-fraction", type=float, default=None)
    parser.add_argument("--smooth-fraction", type=float, default=None)
    parser.add_argument("--min-area-fraction", type=float, default=None)
    
    args = parser.parse_args()

    input_path = INPUT_DIR / args.image
    output_path = OUTPUT_DIR / f"{input_path.stem}_annotated{input_path.suffix}"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read the input image
    img = cv2.imread(str(input_path))
    if img is None:
        raise FileNotFoundError(f"Error: Could not read image from {input_path}")

    # Detect shapes in the image
    detections = detect_shapes(img)

    # Calculate depth and 3D coordinates for the most circular shape
    circle = max(detections, key=circleness)
    depth = calculate_depth(circle, img.shape)
    locations = [{**d, "position": calculate_coords(d, depth, img.shape)} for d in detections]

    # Draw detections on the image
    annotated_img = draw_detections(img, locations)

    # Save the annotated image
    cv2.imwrite(str(output_path), annotated_img)
    print(f"Annotated image saved to {output_path}")

if __name__ == "__main__":
    main()