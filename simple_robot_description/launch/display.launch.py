import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('simple_robot_description')

    # Path to the URDF file
    urdf_file = os.path.join(pkg_dir, 'urdf', 'simple_robot.urdf')

    # Read the URDF into a string
    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    # Configure launch parameters
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # Create launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    # Robot state publisher node with proper QoS configuration
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
            'qos_overrides./robot_description.publisher.durability': 'transient_local',
            'qos_overrides./robot_description.publisher.reliability': 'reliable'
        }]
    )

    # Joint state publisher node
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
    )

    # Joint state publisher GUI node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # RViz2 node
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_dir, 'rviz', 'urdf_config.rviz')] # Config file path
    )

    # Return the launch description
    return LaunchDescription([
        declare_use_sim_time,
        robot_state_publisher_node,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node
    ])
