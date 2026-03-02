#!/usr/bin/env python3

import math
import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

class DynamicTransformPublisher(Node):
    """
    Node to publish dynamic transforms.
    """

    def __init__(self, frame_id, child_frame_id):
        super().__init__('dynamic_transform_publisher')

        self.frame_id = frame_id
        self.child_frame_id = child_frame_id

        # Create a transform broadcaster
        self.broadcaster = TransformBroadcaster(self)

        # Create a timer for publishing transforms
        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz

        # Starting values
        self.theta = 0.0

        self.get_logger().info(f'Publishing dynamic transform: {frame_id} -> {child_frame_id}')

    def timer_callback(self):
        """Publish a transform that follows a circular path."""
        # Create transform
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg() # Get current time for timestamp
        t.header.frame_id = self.frame_id
        t.child_frame_id = self.child_frame_id

        # Set position - circular motion
        t.transform.translation.x = math.cos(self.theta)
        t.transform.translation.y = math.sin(self.theta)
        t.transform.translation.z = 0.0

        # Set orientation - face direction of travel
        q_z = math.sin((self.theta + math.pi/2)/2.0)
        q_w = math.cos((self.theta + math.pi/2)/2.0)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = q_z
        t.transform.rotation.w = q_w

        # Publish transform
        self.broadcaster.sendTransform(t)

        # Update angle for next iteration
        self.theta += 0.02
        if self.theta > 2*math.pi:
            self.theta -= 2*math.pi

def main():
    if len(sys.argv) < 3:
        print("Usage: dynamic_transform_publisher parent_frame child_frame")
        return

    rclpy.init()
    node = DynamicTransformPublisher(sys.argv[1], sys.argv[2])
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
