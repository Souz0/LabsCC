"""Launch file for the robot state publisher."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('simple_robot_description')

    # Create launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    urdf_file_name = LaunchConfiguration('urdf_file')

    # Default URDF file path as a string
    default_urdf_path = os.path.join(pkg_dir, 'urdf', 'simple_robot_gazebo.urdf')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    declare_urdf_file = DeclareLaunchArgument(
        'urdf_file',
        default_value='simple_robot_gazebo.urdf',
        description='URDF file name (within the urdf directory)'
    )

    # Instead of using os.path.join with LaunchConfiguration
    # Use the default path directly for Command substitution
    robot_description_command = Command(['xacro ', default_urdf_path])

    # Create the robot state publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_command,
            'use_sim_time': use_sim_time,
            'qos_overrides./robot_description.publisher.durability': 'transient_local',
            'qos_overrides./robot_description.publisher.reliability': 'reliable'
        }]
    )

    # Return the launch description
    return LaunchDescription([
        declare_use_sim_time,
        declare_urdf_file,
        robot_state_publisher_node
    ])
