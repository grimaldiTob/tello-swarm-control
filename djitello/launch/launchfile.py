from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tello',
            namespace='tello',
            executable='swarm',
            name='swarm'
        ),
        Node(
            package='tello',
            namespace='controller',
            executable='controller',
            name='controller'
        )
    ])