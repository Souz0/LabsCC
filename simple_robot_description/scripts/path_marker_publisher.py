#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA
from tf2_ros import TransformListener, Buffer
import tf2_ros

class PathMarkerPublisher(Node):
    """
    Node to publish a visualisation marker showing the robot's path.
    """

    def __init__(self):
        super().__init__('path_marker_publisher')

        # Create a transform listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create a marker publisher
        self.marker_publisher = self.create_publisher(
            Marker,
            'visualization_marker',
            10
        )

        # Parameters
        self.declare_parameter('update_rate', 10.0)  # Hz
        self.declare_parameter('marker_scale', 0.05)  # Size of the path line
        # Calculate the number of points needed for one revolution
        # This is based on the robot's motion in the dynamic_transform_publishe>
        # where theta is incremented by 0.02 each timer call at 20Hz
        # but, since it is sampled at 10Hz, the sampled increment is actually 0>
        # A full revolution is 2π radians (approximately 6.28)
        points_per_revolution = int(2 * math.pi / 0.04)  # 0.04 is the sampled theta increment
        self.declare_parameter('path_length', points_per_revolution)  # Number of points to keep in the path
        self.path_length = self.get_parameter('path_length').get_parameter_value().integer_value

        self.update_rate = self.get_parameter('update_rate').get_parameter_value().double_value
        self.marker_scale = self.get_parameter('marker_scale').get_parameter_value().double_value
        self.path_length = self.get_parameter('path_length').get_parameter_value().integer_value

        # Create a timer for publishing markers
        self.timer = self.create_timer(1.0 / self.update_rate, self.timer_callback)

        # Store path points
        self.path_points = []

        self.get_logger().info('Path marker publisher started')

    def timer_callback(self):
        """Update and publish the path marker."""
        try:
            # Get the current position of base_link in the world frame
            transform = self.tf_buffer.lookup_transform('world', 'base_link', rclpy.time.Time(seconds=0))

            # Create a point from the transform
            point = Point()
            point.x = transform.transform.translation.x
            point.y = transform.transform.translation.y
            point.z = transform.transform.translation.z

            # Add the point to the path
            self.path_points.append(point)

            # Keep only the most recent points
            if len(self.path_points) > self.path_length:
                self.path_points = self.path_points[-self.path_length:]

            # Create and publish a path marker
            marker = self.create_path_marker(transform)
            self.marker_publisher.publish(marker)

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().warning(f'Could not transform from world to base_link: {str(e)}')

    def create_path_marker(self):
        """Create a line strip marker for the robot's path."""
        marker = Marker()
        marker.header.frame_id = 'world'
        marker.header.stamp = rclpy.time.Time().to_msg()  # Use ROSTIME
        marker.ns = 'robot_path'
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD

        # Use stored points and add current robot position directly
        points_to_display = list(self.path_points)

        # If we have a current transform, add the exact current position as the last point
        if current_transform is not None:
            current_point = Point()
            current_point.x = current_transform.transform.translation.x
            current_point.y = current_transform.transform.translation.y
            current_point.z = current_transform.transform.translation.z
            points_to_display.append(current_point)

        # Set the points in the line strip
        marker.points = points_to_display

        # Line width
        marker.scale.x = self.marker_scale

        # Gradient color along the path (from red to green)
        marker.colors = []
        for i in range(len(points_to_display)):
            color = ColorRGBA()
            # Oldest points are red, newest are green
            ratio = float(i) / max(1, len(points_to_display) - 1)
            color.r = 1.0 - ratio
            color.g = ratio
            color.b = 0.0
            color.a = 0.8
            marker.colors.append(color)

        # If no points yet, set a default color
        if not marker.colors:
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.8

        return marker


def main():
    rclpy.init()
    node = PathMarkerPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
