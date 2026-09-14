import cv2
import numpy as np
import argparse
from pathlib import Path
from shape_detector.detector import detect_shapes
from shape_detector.visualize import draw_detections
from tqdm import tqdm
from shape_detector.geometry import calculate_depth, calculate_coords, circleness, find_reference_circle


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "media" / "input"
OUTPUT_DIR = PROJECT_ROOT / "media" / "output"

def main():
    parser = argparse.ArgumentParser(description="Detect shapes in a video and save the annotated output.")
    parser.add_argument("video", type=str, help="Filename of a video in media/input/")
    parser.add_argument("--var-fraction", type=float, default=None)
    parser.add_argument("--smooth-fraction", type=float, default=None)
    parser.add_argument("--min-area-fraction", type=float, default=None)
    
    args = parser.parse_args()

    input_path = INPUT_DIR / args.video
    output_path = OUTPUT_DIR / f"{input_path.stem}_annotated{input_path.suffix}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise IOError("Cannot open video")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    if not writer.isOpened():
        raise IOError("Cannot open video writer")

    last_depth = None
    # process each frame of the video (show progress bar using tqdm)
    with tqdm(total=total_frames if total_frames > 0 else None, desc="Processing", unit="frame") as pbar:
        while True:
            # read a frame from the video
            ok, frame = cap.read()
            if not ok:
                break

            # detect shapes in the frame and find the reference circle
            detections = detect_shapes(frame)
            ref_circle = find_reference_circle(detections, frame.shape)

            # if a reference circle is found, calculate its depth and use it to compute 3D coordinates for all detections
            if ref_circle is not None:
                last_depth = calculate_depth(ref_circle, frame.shape)
            if last_depth is not None:
                locations = [{**d, "position": calculate_coords(d, last_depth, frame.shape)}
                        for d in detections]
            else:
                locations = detections

            # draw detections on the frame, and write the frame to output
            annotated_frame = draw_detections(frame, locations)
            writer.write(annotated_frame)

            pbar.update(1)

    cap.release()
    writer.release()

if __name__ == "__main__":
    main()