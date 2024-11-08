import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    voris_description_dir = get_package_share_directory('voris_description')
    urdf_file = os.path.join(voris_description_dir, 'urdf','bluerov2',
                             'simple_bluerov2_heavy.urdf')


    return LaunchDescription([

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(voris_description_dir, 'cfg', 'orca_config.rviz')],
            parameters=[{'robot_description': open(urdf_file).read()}]
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_file).read()}]
        ),

        ExecuteProcess(
            cmd=['/opt/ros/humble/lib/tf2_ros/static_transform_publisher',
                 '--frame-id', 'map',
                 '--child-frame-id', 'base_link'],
            output='screen',
        ),

        Node(
            package='voris_description',
            executable='odom2tf.py',
            name='odom2tf',
            output='screen',
            remappings=[
                ('/odometry', '/model/bluerov2/odometry')
            ]
        )

    ])
