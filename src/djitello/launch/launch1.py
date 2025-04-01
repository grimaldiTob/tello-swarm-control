import launch
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='djitello',
            executable='tello',  
            name= 'tello1'
        ),
        launch_ros.actions.Node(
            package='djitello',
            executable='controller',
            name='controller'
        )
    ])