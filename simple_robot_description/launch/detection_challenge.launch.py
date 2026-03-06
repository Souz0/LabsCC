# launch/detection_challenge.launch.py

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    yolo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('yolo_bringup'), '/launch/yolo.launch.py'
        ]),
        launch_arguments={
            # TODO: Replace [USERNAME] with your username
            'model': '/home/[USERNAME]/ros2_ws/custom_models/best.pt',
            'device': 'cpu',
            'threshold': '0.5',
            'input_image_topic': '/camera/image_raw',
        }.items()
    )

    return LaunchDescription([
        yolo_launch,
    ])