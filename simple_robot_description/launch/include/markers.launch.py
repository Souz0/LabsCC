"""Launch file for visualization markers."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    # Create launch configuration variables
    use_markers = LaunchConfiguration('use_markers', default='true')
    marker_scale = LaunchConfiguration('marker_scale', default='0.2')
    update_rate = LaunchConfiguration('update_rate', default='10.0')

    # Declare launch arguments
    declare_use_markers = DeclareLaunchArgument(
        'use_markers',
        default_value='true',
        description='Launch marker publisher if true'
    )

    declare_marker_scale = DeclareLaunchArgument(
        'marker_scale',
        default_value='0.2',
        description='Scale of visualization markers'
    )

    declare_update_rate = DeclareLaunchArgument(
        'update_rate',
        default_value='10.0',
        description='Update rate for markers (Hz)'
    )

    # Create the marker publisher node
    marker_publisher = Node(
        package='simple_robot_description',
        executable='frame_marker_publisher.py',
        name='frame_marker_publisher',
        output='screen',
        parameters=[{
            'marker_scale': marker_scale,
            'update_rate': update_rate
        }],
        condition=IfCondition(use_markers)
    )

    # Create the path marker publisher node
    path_marker_publisher = Node(
        package='simple_robot_description',
        executable='path_marker_publisher.py',
        name='path_marker_publisher',
        output='screen',
        parameters=[{
            'marker_scale': marker_scale,
            'update_rate': update_rate,
            'path_length': 50  # Override number of points in the path
        }],
        condition=IfCondition(use_markers)
    )

    # Return the launch description
    return LaunchDescription([
        declare_use_markers,
        declare_marker_scale,
        declare_update_rate,
        marker_publisher,
        path_marker_publisher
    ])
