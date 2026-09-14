import numpy as np
import cv2
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point32, Polygon
from rclpy.node import Node
from sensor_msgs.msg import Image


IMAGE_TOPIC = "camera/image_raw"
QUEUE_SIZE = 10
FALLBACK_FPS = 30.0

class ImagePublisher(Node):
    def __init__(self) -> None:
        # initialize the ROS2 node and set up video capture, publisher, and timer
        super().__init__("image_publisher")
        self.declare_parameter("video_path", "")
        self.declare_parameter("loop", True)

        video_path = self.get_parameter("video_path").value
        self.loop = self.get_parameter("loop").value

        self.capture = cv2.VideoCapture(video_path)
        if not self.capture.isOpened():
            raise RuntimeError(f"could not open video: {video_path}")

        fps = self.capture.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = FALLBACK_FPS

        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, IMAGE_TOPIC, QUEUE_SIZE)
        self.timer = self.create_timer(1.0 / fps, self.publish_frame)
        self.get_logger().info(f"publishing {video_path} at {fps:.1f} fps")

    def publish_frame(self) -> None:
        # read a frame from the video capture and publish it as a ROS2 Image message
        ok, frame = self.capture.read()
        if not ok:
            if self.loop:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return
            self.get_logger().info("end of video, stopping")
            self.timer.cancel()
            return

        message = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = "camera"
        self.publisher.publish(message)

    def destroy_node(self) -> bool:
        # release the video capture and destroy the ROS2 node
        self.capture.release()
        return super().destroy_node()


def main(args=None) -> None:
    # main function
    rclpy.init(args=args)
    node = ImagePublisher()
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
