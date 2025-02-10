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
    urdf_file = os.path.join(voris_description_dir, 'urdf', 'laboratory', 'sm3_laser.urdf')

    return LaunchDescription([
        DeclareLaunchArgument(name='rvizconfig', default_value='sm3_config.rviz', description='Absolute path to rviz config file'),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', PathJoinSubstitution([
                FindPackageShare('voris_description'), 'cfg', LaunchConfiguration('rvizconfig')])],
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_file).read()}],
        ),

        ExecuteProcess(
            cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
                 '--frame-id', 'map',
                 '--child-frame-id', 'base_link'],
            output='screen',
        ),
    ])
