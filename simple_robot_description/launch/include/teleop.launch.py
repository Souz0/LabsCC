"""Launch file for keyboard teleoperation."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Create launch configuration variables
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic', default='/cmd_vel')

    # Declare launch arguments
    declare_cmd_vel_topic = DeclareLaunchArgument(
        'cmd_vel_topic',
        default_value='/cmd_vel',
        description='Topic for velocity commands'
    )

    # Create the teleop node
    teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',  # Launch in a separate terminal window
        parameters=[],
        remappings=[
            ('/cmd_vel', cmd_vel_topic)
        ]
    )

    # Return the launch description
    return LaunchDescription([
        declare_cmd_vel_topic,
        teleop_node
    ])
