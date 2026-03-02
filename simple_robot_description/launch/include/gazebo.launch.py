"""Launch file for Gazebo simulation."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('simple_robot_description')

    # Create launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = LaunchConfiguration('world_file', default=os.path.join(pkg_dir, 'worlds', 'diff_drive', 'diff_drive.sdf'))
    use_gazebo_gui = LaunchConfiguration('use_gazebo_gui', default='true')
    robot_name = LaunchConfiguration('robot_name', default='simple_robot')
    x_pos = LaunchConfiguration('x_pos', default='0.0')
    y_pos = LaunchConfiguration('y_pos', default='0.0')
    z_pos = LaunchConfiguration('z_pos', default='0.1')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    declare_world_file = DeclareLaunchArgument(
        'world_file',
        default_value=os.path.join(pkg_dir, 'worlds', 'diff_drive', 'diff_drive.sdf'),
        description='Path to world file'
    )

    declare_use_gazebo_gui = DeclareLaunchArgument(
        'use_gazebo_gui',
        default_value='true',
        description='Use Gazebo GUI if true'
    )

    declare_robot_name = DeclareLaunchArgument(
        'robot_name',
        default_value='simple_robot',
        description='Name of the robot'
    )

    declare_x_pos = DeclareLaunchArgument(
        'x_pos',
        default_value='0.0',
        description='X position for robot spawning'
    )

    declare_y_pos = DeclareLaunchArgument(
        'y_pos',
        default_value='0.0',
        description='Y position for robot spawning'
    )

    declare_z_pos = DeclareLaunchArgument(
        'z_pos',
        default_value='0.1',
        description='Z position for robot spawning'
    )

    # Create the Gazebo launch command
    gazebo_cmd = [
        'ign', 'gazebo',
        '-r', world_file
    ]

    gazebo_process = ExecuteProcess(
        cmd=gazebo_cmd,
        output='screen'
    )

    # Spawn entity using ros_gz_sim
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_name,
            '-topic', 'robot_description',
            '-x', x_pos,
            '-y', y_pos,
            '-z', z_pos
        ],
        output='screen'
    )

    # Set up bridges between ROS2 and Gazebo
    bridge_params = os.path.join(pkg_dir, 'config', 'gz_bridge.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p', f'config_file:={bridge_params}',
        ]
    )

    bridge_camera_image = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image_raw"]
    )

    # Return the launch description
    return LaunchDescription([
        declare_use_sim_time,
        declare_world_file,
        declare_use_gazebo_gui,
        declare_robot_name,
        declare_x_pos,
        declare_y_pos,
        declare_z_pos,
        gazebo_process,
        spawn_entity,
        ros_gz_bridge,
        bridge_camera_image
    ])
