"""Launch file for transform publishers."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():
    # Create launch configuration variables
    use_static_tf = LaunchConfiguration('use_static_tf', default='true')
    use_dynamic_tf = LaunchConfiguration('use_dynamic_tf', default='false')

    # Declare launch arguments
    declare_use_static_tf = DeclareLaunchArgument(
        'use_static_tf',
        default_value='true',
        description='Launch static transform publisher if true'
    )

    declare_use_dynamic_tf = DeclareLaunchArgument(
        'use_dynamic_tf',
        default_value='false',
        description='Launch dynamic transform publisher if true'
    )

    # Create the static transform publisher using the built-in tf2_ros tool
    static_world_to_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_odom_broadcaster',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom'],
        condition=IfCondition(use_static_tf)
    )

    # Create the dynamic transform publisher using our custom node
    dynamic_odom_to_base = Node(
        package='simple_robot_description',
        executable='dynamic_transform_publisher.py',
        name='odom_base_broadcaster',
        output='screen',
        arguments=['odom', 'base_link'],
        condition=IfCondition(use_dynamic_tf)
    )

    # Fallback static transform when dynamic is disabled but static is enabled
    # This ensures the TF tree remains connected
    static_odom_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_odom_base_broadcaster',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_link'],
        # Only use this when static=true AND dynamic=false
        condition=UnlessCondition(use_dynamic_tf)
    )

    # Return the launch description
    return LaunchDescription([
        declare_use_static_tf,
        declare_use_dynamic_tf,
        static_world_to_odom,
        dynamic_odom_to_base,
        static_odom_to_base
    ])
