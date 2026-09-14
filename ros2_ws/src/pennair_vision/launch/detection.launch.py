from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    # create a launch description for the ROS2 nodes
    video_path = LaunchConfiguration("video_path")

    return LaunchDescription([
        DeclareLaunchArgument(
            "video_path",
            default_value="/work/media/input/video.mp4",
            description="video file the publisher streams",
        ),
        Node(
            package="pennair_vision",
            executable="image_publisher",
            name="image_publisher",
            parameters=[{"video_path": video_path, "loop": True}],
            output="screen",
        ),
        Node(
            package="pennair_vision",
            executable="detector_node",
            name="detector_node",
            output="screen",
        ),
    ])