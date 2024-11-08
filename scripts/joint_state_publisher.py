import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import ModelState
from sensor_msgs.msg import JointState
from gazebo_msgs.srv import GetJointProperties

class GazeboJointStatePublisher(Node):
    def __init__(self):
        super().__init__('gazebo_joint_state_publisher')
        self.joint_state_publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.client = self.create_client(GetJointProperties, '/gazebo/get_joint_properties')

        # Waiting for the service to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        self.timer = self.create_timer(0.1, self.publish_joint_state)

    def publish_joint_state(self):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()

        # List the joints in your robot
        joint_names = ['right_camera_joint', 'left_camera_joint', 'joint_3']  # Change based on your robot

        joint_state_msg.name = joint_names
        joint_state_msg.position = []

        # Request the joint state from Gazebo
        for joint in joint_names:
            request = GetJointProperties.Request()
            request.joint_name = joint
            response = self.client.call(request)

            # Append the joint position (assuming single degree of freedom)
            joint_state_msg.position.append(response.position[0])

        # Publish the joint state
        self.joint_state_publisher.publish(joint_state_msg)

def main(args=None):
    rclpy.init(args=args)
    node = GazeboJointStatePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()