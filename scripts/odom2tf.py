#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import tf2_ros
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped

class Odom2TF(Node):
    def __init__(self):
        super().__init__('odometry_to_tf')
        self.subscriber = self.create_subscription(Odometry, '/odometry', self.handle_odometry, 10)
        self.br = tf2_ros.TransformBroadcaster(self)

    def handle_odometry(self, msg):
        # Create the transform message
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = "map"    # Parent frame (global)
        t.child_frame_id = "base_link" # Child frame (robot base)

        # Set the position from the odometry message
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z

        # Set the orientation from the odometry message
        t.transform.rotation = msg.pose.pose.orientation

        # Broadcast the transform
        self.br.sendTransform(t)

def odometry_to_tf(args=None):
    rclpy.init(args=args)

    odom2tf_sub = Odom2TF()  # Corrected to create an instance of the Odom2TF class
    rclpy.spin(odom2tf_sub)

    # Destroy the node explicitly
    odom2tf_sub.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    odometry_to_tf()
