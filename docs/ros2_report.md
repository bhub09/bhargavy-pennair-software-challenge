# ROS2 Report

## 1. Architecture
There are two nodes in this particular design: `image_publisher` reads the video and publishes `sensor_msgs/Image` on `camera/image_raw`, while `detector_node` subscribes, runs `detect_shapes` along with geometry functions, and publishes `pennair_msgs/ShapeDetectionArray` on `shapes/detections`. The architecture was designed with this split between shape detection and image publishing for several reasons. The important ones are modularity, diagnostics, and independence. On the modularity end, `image_publisher` could be replaced with a camera driver. Having two separate nodes also isolates image capture failure and detection failure, allowing for safeguards to be implemented in the event of either. Isolation also makes it easy to pinpoint where the specific issue in the pipeline is. Finally, the independence of the nodes means that speed issues with detection can't stall image capture.

## 2. Reason for choosing topics
Topics are chosen for communication as opposed to services or actions, as it is best suited for a continuous sensor stream, and the subscriber system allows for multiple consumers (i.e. recorder, visualizer, controller) to attach with no changes to the data publishing. 

## 3. Message design
```
ShapeDetection
  geometry_msgs/Point32   -> center
  geometry_msgs/Polygon   -> outline
  float32                 -> area
  geometry_msgs/Point32   -> position

ShapeDetectionArray
  std_msgs/Header         -> header
  ShapeDetection[]        -> detections
```
The `Point32` data type is chosen over `Point` because pixel coordinates don't need extra precision, and `Polygon` (used for the outline) uses `Point32`. `Polygon` is used for the outline, as it is a standard type that can be interpreted without knowing conventions. Additionally, there is one header on the array, and not per detection, as all detections in a frame/image share a timestamp and frame_id (making duplication a waste). 

## 4. Making `pennair_msgs` a separate package
Message generation runs through `rosidl`, which is CMake-based, as `ament_python` can't generate interfaces. Thus, `pennair_msgs` is `ament_cmake` while `pennair_vision` is `ament_python`. 

## 5. Implementation
`cv_bridge` converts between `sensor_msgs/Image` and numpy arrays. Additionally, there are float casts on every numeric field, as `float32` rejects float64. A timer set at `1/fps` drives publishing, either going to frame 0 at the end of the video or canceling the timer. Finally `last_depth` is carried in the node.

## 6. Performance
```
/camera/image_raw     ~12 Hz    min 0.024s  max 0.505s  std 0.113s
/shapes/detections    17.7 Hz   min 0.053s  max 0.060s  std 0.0016s
```
Note that the 12 Hz rate is not the publisher's actual rate, as `ros2 topic hz` is deserializing 6 MB per message. Also, standard deviation findings of the detections vs image capture shows there may be a bottleneck.

## 7. Queue
The queue depth is 10, with a publisher frequency of 30 Hz, and a detector frequency of 18 Hz. Frames are dropped when the queue fills. This was to guarantee fresh frames.

## 8. Limitations
The raw image is roughly 6 MB per message, and a compression method (either using nodes or the `CompressedImage` type) would help in this process. Additionally, detector threshold are not exposed as ROS parameters, and can't be tuned at launch. Finally, the setup is done through manual commands, while a Dockerfile would have made it reproducible.