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


        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_file_simple).read()}],
        ),

        ExecuteProcess(
            cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
                 '--frame-id', 'map',
                 '--child-frame-id', 'base_link'],
            output='screen',
        ),

        ExecuteProcess(
            cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
                 '--roll', '-1.5707',
                 '--yaw', '-1.5707',
                 '--frame-id', 'map',
                 '--child-frame-id', 'orbslam3'],
            output='screen',
        ),
    ])
