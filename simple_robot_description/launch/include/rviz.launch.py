"""Launch file for RViz visualisation."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('simple_robot_description')

    # Create launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_rviz = LaunchConfiguration('use_rviz', default='true')
    rviz_config = LaunchConfiguration('rviz_config', default=os.path.join(pkg_dir, 'rviz', 'urdf_config.rviz'))

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz if true'
    )

    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=os.path.join(pkg_dir, 'rviz', 'urdf_config.rviz'),
        description='Path to RViz config file'
    )

    # Create the RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz)
    )

    # Return the launch description
    return LaunchDescription([
        declare_use_sim_time,
        declare_use_rviz,
        declare_rviz_config,
        rviz_node
    ])
