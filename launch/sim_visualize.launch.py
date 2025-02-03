import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    voris_description_dir = get_package_share_directory('voris_description')
    urdf_file = os.path.join(voris_description_dir, 'urdf', 'bluerov2', 'bluerov2_heavy.urdf')
    urdf_file_simple = os.path.join(voris_description_dir, 'urdf', 'bluerov2', 'simple_bluerov2_heavy.urdf')

    return LaunchDescription([
        DeclareLaunchArgument(name='gui', default_value='true', choices=['true', 'false'],
                              description='Enable joint_state_publisher_gui'),

        DeclareLaunchArgument(name='simple_urdf', default_value='true', choices=['true', 'false'],
                              description='Open ROV with or without propellers'),

        DeclareLaunchArgument(name='rvizconfig', default_value='sim_config.rviz',
                              description='Absolute path to rviz config file'),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', PathJoinSubstitution([
                FindPackageShare('voris_description'), 'cfg', LaunchConfiguration('rvizconfig')])],
            condition=IfCondition(LaunchConfiguration('gui'))
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_file_simple).read()}],
            condition=IfCondition(LaunchConfiguration('simple_urdf'))
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_file).read()}],
            condition=UnlessCondition(LaunchConfiguration('simple_urdf')),
        ),

        # Node(
        #     package='voris_description',
        #     executable='odom2tf.py',
        #     name='odom2tf',
        #     output='screen',
        #     remappings=[
        #         ('/odometry', '/model/bluerov2_heavy/odometry')
        #     ]
        # ),
        Node(
            package='voris_description',
            executable='joint_state_publisher.py',
            name='gz_joint_state_publisher',
            output='screen',
            condition=UnlessCondition(LaunchConfiguration('simple_urdf')),
        ),
        # Publish joint position from thrusters
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='gz_bridge',
            output='screen',
            arguments=[
                '/model/bluerov2_heavy/joint/thruster1_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster2_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster3_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster4_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster5_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster6_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster7_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/bluerov2_heavy/joint/thruster8_joint/ang_vel@std_msgs/msg/Float64@gz.msgs.Double'
            ],
            condition=UnlessCondition(LaunchConfiguration('simple_urdf')),
        ),

        # Node(
        #     package='voris_description',
        #     executable='joint_state_publisher.py',
        #     name='gz_joint_state',
        #     output='screen'
        # ),

        # ExecuteProcess(
        #     cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
        #          '--frame-id', 'map',
        #          '--child-frame-id', 'base_link'],
        #     output='screen',
        # ),

        # ExecuteProcess(
        #     cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
        #          '--frame-id', 'map',
        #          '--child-frame-id', 'odom'],
        #     output='screen',
        # ),

    ])
