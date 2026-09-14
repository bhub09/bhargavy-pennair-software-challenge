import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point32, Polygon
from rclpy.node import Node
from sensor_msgs.msg import Image

from pennair_msgs.msg import ShapeDetection as ShapeDetectionMsg
from pennair_msgs.msg import ShapeDetectionArray
from shape_detector.detector import detect_shapes
from shape_detector.geometry import (
    ShapeDetection3D,
    calculate_coords,
    calculate_depth,
    find_reference_circle,
)

IMAGE_TOPIC = "camera/image_raw"
DETECTION_TOPIC = "shapes/detections"
QUEUE_SIZE = 10


class DetectorNode(Node):
    def __init__(self) -> None:
        # initialize the ROS2 node and set up the publisher and subscription
        super().__init__("detector_node")
        self.bridge = CvBridge()
        self.last_depth: float | None = None
        self.publisher = self.create_publisher(
            ShapeDetectionArray, DETECTION_TOPIC, QUEUE_SIZE
        )
        self.subscription = self.create_subscription(
            Image, IMAGE_TOPIC, self.handle_frame, QUEUE_SIZE
        )

    def handle_frame(self, message: Image) -> None:
        # convert the ROS2 Image message to a CV2 image, detect shapes, and publish the detections
        frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
        detections = detect_shapes(frame)

        circle = find_reference_circle(detections, frame.shape)
        if circle is not None:
            self.last_depth = calculate_depth(circle, frame.shape)

        array = ShapeDetectionArray()
        array.header = message.header
        array.detections = [
            self._to_message(detection, frame.shape) for detection in detections
        ]
        self.publisher.publish(array)

    def _to_message(self, detection: ShapeDetection3D, frame_shape) -> ShapeDetectionMsg:
        # convert a ShapeDetection3D object to a ROS2 ShapeDetection message
        message = ShapeDetectionMsg()
        cx, cy = detection["center"]
        message.center = Point32(x=float(cx), y=float(cy), z=0.0)
        message.area = float(detection["area"])
        message.outline = Polygon(
            points=[
                Point32(x=float(px), y=float(py), z=0.0)
                for px, py in detection["outline"]
            ]
        )
        if self.last_depth is not None:
            x, y, z = calculate_coords(detection, self.last_depth, frame_shape)
            message.position = Point32(x=float(x), y=float(y), z=float(z))
        return message

# main function
def main(args=None) -> None:
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()