#!/usr/bin/env python3

import copy
import math
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA
from tf2_ros import TransformListener, Buffer
import tf2_ros

class FrameMarkerPublisher(Node):
    """
    Node to publish visualization markers for coordinate frames.
    """

    def __init__(self):
        super().__init__('frame_marker_publisher')

        # Create a transform listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create a marker publisher
        self.marker_publisher = self.create_publisher(
            MarkerArray,
            'visualization_marker_array',
            10
        )

        # Parameters
        self.declare_parameter('update_rate', 40.0)  # Hz
        self.declare_parameter('marker_scale', 0.2)  # Size of the markers

        self.update_rate = self.get_parameter('update_rate').get_parameter_value().double_value
        self.marker_scale = self.get_parameter('marker_scale').get_parameter_value().double_value

        # Create a timer for publishing markers
        self.timer = self.create_timer(1.0 / self.update_rate, self.timer_callback)

        # Frames of interest
        self.frames = ['world', 'base_link', 'camera_link', 'right_wheel', 'left_wheel']

        self.get_logger().info('Frame marker publisher started')

    def timer_callback(self):
        """Publish markers for each frame."""
        # Create a marker array
        marker_array = MarkerArray()

        # Create markers for each frame
        for frame_id in self.frames:
            try:
                # Skip if this is the world frame (no parent)
                if frame_id == 'world':
                    # Still create a marker for the world frame
                    markers = self.create_frame_marker(frame_id, 'world')
                    # Add all returned markers to the array
                    marker_array.markers.extend(markers)
                    continue

                # Get the transform from the parent frame to this frame
                transform = self.tf_buffer.lookup_transform('world', frame_id, rclpy.time.Time(seconds=0))

                # Create a marker for this frame
                markers = self.create_frame_marker(frame_id, 'world', transform)
                # Add all returned markers to the array
                marker_array.markers.extend(markers)

                # Create a line to the parent
                parent_frame = 'unknown'
                try:
                    # Try to find the parent frame by looking up transforms
                    for potential_parent in self.frames:
                        if potential_parent == frame_id:
                            continue
                        try:
                            self.tf_buffer.lookup_transform(potential_parent, frame_id, rclpy.time.Time(seconds=0))
                            parent_frame = potential_parent
                            break
                        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                            continue

                    # If found a parent, create a line
                    if parent_frame != 'unknown':
                        parent_transform = self.tf_buffer.lookup_transform('world', parent_frame, rclpy.time.Time(seconds=0))
                        marker_array.markers.append(self.create_connection_marker(
                            frame_id, parent_frame, transform, parent_transform
                        ))
                except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                    # Ignore errors finding the parent
                    pass

            except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
                self.get_logger().warning(f'Could not transform from world to {frame_id}: {str(e)}')

        # Publish the marker array
        self.marker_publisher.publish(marker_array)

    def create_frame_marker(self, frame_id, reference_frame, transform=None):
        """Create a marker to represent a coordinate frame."""
        marker = Marker()
        marker.header.frame_id = reference_frame
        marker.header.stamp = rclpy.time.Time().to_msg() # Use ROSTIME
        marker.ns = 'frames'
        marker.id = hash(frame_id) % 10000  # Simple hash to get a unique ID
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # Set the position based on transform or at origin
        if transform:
            marker.pose.position.x = transform.transform.translation.x
            marker.pose.position.y = transform.transform.translation.y
            marker.pose.position.z = transform.transform.translation.z
            marker.pose.orientation = transform.transform.rotation
        else:
            # For world frame or if no transform is available
            marker.pose.position.x = 0.0
            marker.pose.position.y = 0.0
            marker.pose.position.z = 0.0
            marker.pose.orientation.w = 1.0

        # Set the scale
        marker.scale.x = self.marker_scale
        marker.scale.y = self.marker_scale
        marker.scale.z = self.marker_scale

        # Set colour based on the frame_id to make each frame distinct
        colors = {
            'world': [0.5, 0.5, 0.5],  # Grey
            'base_link': [0.0, 1.0, 0.0],  # Green
            'camera_link': [0.0, 0.0, 1.0],  # Blue
            'right_wheel': [1.0, 1.0, 0.0],  # Yellow
            'left_wheel': [0.0, 1.0, 1.0],   # Cyan
        }

        color = colors.get(frame_id, [1.0, 1.0, 1.0])  # Default to white
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = 1.0

        # Create a text marker for this frame
        text_marker = Marker()
        text_marker.header = marker.header
        text_marker.ns = 'frame_texts'
        text_marker.id = marker.id + 1000  # Offset to avoid ID collision
        text_marker.type = Marker.TEXT_VIEW_FACING
        text_marker.action = Marker.ADD
        text_marker.pose = marker.pose
        # Deep copy the pose to avoid modifying the original marker pose
        text_marker.pose = copy.deepcopy(marker.pose)
        text_marker.pose.position.z += self.marker_scale * 1.5  # Place text above sphere
        text_marker.scale.z = self.marker_scale * 0.5  # Text size
        text_marker.color.r = 1.0
        text_marker.color.g = 1.0
        text_marker.color.b = 1.0
        text_marker.color.a = 1.0
        text_marker.text = frame_id

        # Return both markers so they can be added to the marker array
        return [marker, text_marker]

    def create_connection_marker(self, child_frame, parent_frame, child_transform, parent_transform):
        """Create a line marker connecting parent and child frames."""
        marker = Marker()
        marker.header.frame_id = 'world'
        marker.header.stamp = rclpy.time.Time().to_msg()  # Use ROSTIME
        marker.ns = 'connections'
        marker.id = hash(f"{parent_frame}_{child_frame}") % 10000
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD

        # Line from parent to child
        start_point = Point()
        start_point.x = parent_transform.transform.translation.x
        start_point.y = parent_transform.transform.translation.y
        start_point.z = parent_transform.transform.translation.z

        end_point = Point()
        end_point.x = child_transform.transform.translation.x
        end_point.y = child_transform.transform.translation.y
        end_point.z = child_transform.transform.translation.z

        marker.points = [start_point, end_point]

        # Line width
        marker.scale.x = self.marker_scale * 0.1  # Thinner than the spheres

        # Line color - light grey
        marker.color.r = 0.7
        marker.color.g = 0.7
        marker.color.b = 0.7
        marker.color.a = 0.7

        return marker


def main():
    rclpy.init()
    node = FrameMarkerPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
