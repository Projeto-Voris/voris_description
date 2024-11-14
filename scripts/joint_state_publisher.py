#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64  # Assuming ang_vel is of Float64 type
import math

class GazeboJointStatePublisher(Node):
    def __init__(self):
        super().__init__('gazebo_joint_state_publisher')
        self.joint_state_publisher = self.create_publisher(JointState, '/joint_states', 10)

        # Define the joint names and corresponding Gazebo topics
        self.joint_names = [
            'thruster1_joint', 'thruster2_joint', 'thruster3_joint', 'thruster4_joint',
            'thruster5_joint', 'thruster6_joint', 'thruster7_joint', 'thruster8_joint'
        ]

        # Initialize dictionaries to store the latest velocities and positions
        self.joint_velocities = {joint: 0.0 for joint in self.joint_names}
        self.joint_positions = {joint: 0.0 for joint in self.joint_names}
        self.last_update_time = self.get_clock().now()  # Track the last update time for integration

        # Create a subscriber for each joint's ang_vel topic
        for joint in self.joint_names:
            topic_name = f'/model/bluerov2_heavy/joint/{joint}/ang_vel'
            self.create_subscription(Float64, topic_name, self.create_joint_callback(joint), 10)

        # Timer for publishing joint states
        self.timer = self.create_timer(0.1, self.publish_joint_state)

    def create_joint_callback(self, joint_name):
        # Closure to capture joint_name and update the joint's velocity
        def callback(msg):
            self.joint_velocities[joint_name] = msg.data
        return callback

    def publish_joint_state(self):
        # Get the current time and calculate the time delta
        current_time = self.get_clock().now()
        delta_time = (current_time - self.last_update_time).nanoseconds * 1e-9  # Convert ns to seconds
        self.last_update_time = current_time

        # Update positions based on the velocity and delta time
        for joint, velocity in self.joint_velocities.items():
            # Integrate velocity to update position
            self.joint_positions[joint] += velocity * delta_time

            # Wrap the position to stay within the range [0, 2*pi]
            self.joint_positions[joint] = self.joint_positions[joint] % (2 * math.pi)

        # Create the JointState message
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = current_time.to_msg()
        joint_state_msg.name = list(self.joint_positions.keys())
        joint_state_msg.position = list(self.joint_positions.values())
        joint_state_msg.velocity = list(self.joint_velocities.values())

        # Publish the aggregated joint state
        self.joint_state_publisher.publish(joint_state_msg)

def main(args=None):
    rclpy.init(args=args)
    node = GazeboJointStatePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()