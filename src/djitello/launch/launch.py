import launch
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='djitello',
            executable='tello',  
            name='tello1',
            parameters=[
                {'tello_ip': '192.168.16.112', 'id': '1'}
            ]
        ),
        launch_ros.actions.Node(
            package='djitello',
            executable='tello',
            name='tello2',
            parameters=[
                {'tello_ip': '192.168.16.113', 'id': '2'}
            ]
        ),
        launch_ros.actions.Node(
            package='djitello',
            executable='controller',
            name='controller'
        )
    ])