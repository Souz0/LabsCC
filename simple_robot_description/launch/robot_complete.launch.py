"""Main launch file for the complete robot setup with multiple operation modes."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('simple_robot_description')
    include_dir = os.path.join(pkg_dir, 'launch', 'include')

    # Define paths to URDF file
    urdf_file = os.path.join(pkg_dir, 'urdf', 'simple_robot_gazebo.urdf')

    # Create launch configuration variables
    use_static_tf = LaunchConfiguration('use_static_tf', default='true')
    use_dynamic_tf = LaunchConfiguration('use_dynamic_tf', default='true')
    use_gazebo = LaunchConfiguration('use_gazebo', default='true')
    use_teleop = LaunchConfiguration('use_teleop', default='true')
    world_file = LaunchConfiguration('world_file', default=os.path.join(pkg_dir, 'worlds', 'diff_drive', 'diff_drive.sdf'))
    use_markers = LaunchConfiguration('use_markers', default='true')
    marker_scale = LaunchConfiguration('marker_scale', default='0.2')
    update_rate = LaunchConfiguration('update_rate', default='10.0')
    model_path = LaunchConfiguration(
    'model_path',
    default=os.path.join('/home', os.environ.get('USER', ''), 'ros2_ws', 'custom_models', 'best.pt')
)

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

    declare_use_static_tf = DeclareLaunchArgument(
        'use_static_tf',
        default_value='true',
        description='Launch static transform publisher if true'
    )

    declare_use_dynamic_tf = DeclareLaunchArgument(
        'use_dynamic_tf',
        default_value='true',
        description='Launch dynamic transform publisher if true'
    )
    
    declare_use_gazebo = DeclareLaunchArgument(
        'use_gazebo',
        default_value='true',
        description='Launch Gazebo if true'
    )

    declare_use_teleop = DeclareLaunchArgument(
        'use_teleop',
        default_value='true',
        description='Launch teleop if true'
    )

    declare_world_file = DeclareLaunchArgument(
        'world_file',
        default_value=os.path.join(pkg_dir, 'worlds', 'diff_drive', 'diff_drive.sdf'),
        description='Path to world file'
    )

    declare_model_path = DeclareLaunchArgument(
        'model_path',
    	default_value=os.path.join('/home', os.environ.get('USER', ''), 'ros2_ws', 'custom_models', 'best.pt'),
    	description='Path to the trained YOLO model'
    )

    # Read URDF file content
    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    # ------------------------------------------------------
    # Nodes required for all modes
    # ------------------------------------------------------

    # Robot state publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    # ------------------------------------------------------
    # RViz nodes with different configurations
    # ------------------------------------------------------

    # RViz node for Gazebo mode (with camera)
    rviz_node_gazebo = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_dir, 'rviz', 'urdf_config.rviz')],
        condition=IfCondition(use_gazebo)
    )

    # RViz node for visualisation-only mode (without camera)
    rviz_node_viz_only = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_dir, 'rviz', 'urdf_config_nogazebo.rviz')],
        condition=UnlessCondition(use_gazebo)
    )

    # ------------------------------------------------------
    # Nodes required for ONLY the non-Gazebo visualisation mode
    # ------------------------------------------------------

    # Joint state publisher (used when Gazebo is not running)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=UnlessCondition(use_gazebo)
    )

    # Joint state publisher GUI (used when Gazebo is not running)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=UnlessCondition(use_gazebo)
    )

    # ------------------------------------------------------
    # Nodes required for ONLY the Gazebo simulation mode
    # ------------------------------------------------------

    # Gazebo node
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', world_file],
        output='screen',
        condition=IfCondition(use_gazebo)
    )

    # Spawn entity
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'simple_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen',
        condition=IfCondition(use_gazebo)
    )

    # ROS-Gazebo bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p', f'config_file:={os.path.join(pkg_dir, "config", "gz_bridge.yaml")}',
        ],
        condition=IfCondition(use_gazebo)
    )

    # Camera bridge
    camera_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image_raw"],
        condition=IfCondition(use_gazebo)
    )

    # ------------------------------------------------------
    # Teleop (controlled by use_teleop flag AND use_gazebo flag)
    # ------------------------------------------------------

    # Teleop node - only active when both use_teleop AND use_gazebo are true
    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',
        remappings=[('/cmd_vel', '/cmd_vel')],
        condition=IfCondition(
            PythonExpression([
                '"', use_teleop, '" == "true" and "', use_gazebo, '" == "true"'
            ])
        )
    )
    
    # Include transforms launch file
    transforms_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(include_dir, 'transforms.launch.py')
        ),
        launch_arguments={
            'use_static_tf': use_static_tf,
            'use_dynamic_tf': use_dynamic_tf
        }.items()
    )

    # Include markers launch file
    markers_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(include_dir, 'markers.launch.py')),
        launch_arguments={
            'use_markers': use_markers,
            'marker_scale': marker_scale,
            'update_rate': update_rate
        }.items()
    )

    yolo_launch = IncludeLaunchDescription(
    	PythonLaunchDescriptionSource([
            FindPackageShare('yolo_bringup'), '/launch/yolo.launch.py'
    	]),
    	launch_arguments={
            'model': model_path,
            'device': 'cpu',
            'threshold': '0.5',
            'input_image_topic': '/camera/image_raw',
    	}.items(),
    	condition=IfCondition(use_gazebo)
    )

    # Return the launch description
    return LaunchDescription([
        # Launch arguments
	declare_model_path,
        declare_use_gazebo,
        declare_use_teleop,
        declare_world_file,
        declare_use_static_tf,
        declare_use_dynamic_tf,
        declare_use_markers,
        declare_marker_scale,
        declare_update_rate,    
        # Nodes for all modes
        robot_state_publisher,
        transforms_launch, 	
        markers_launch,
        # RViz nodes (conditionally loaded based on mode)
        rviz_node_gazebo,
        rviz_node_viz_only,
        # Visualisation-only nodes
        joint_state_publisher,
        joint_state_publisher_gui,
        # Gazebo simulation nodes
        gazebo,
        spawn_entity,
        bridge,
        camera_bridge,
	yolo_launch,
        # Teleop
        teleop
    ])