import rclpy
from rclpy.node import Node
import numpy as np
from std_msgs.msg import Header
from geometry_msgs.msg import Point, Quaternion, PoseStamped

class TestNode(Node):

    def __init__(self, frequency=0.01):
        super().__init__("TestNode")
        self.get_logger().info(f"Test node initialized!")

        self.frequency = frequency
        self.pose = [0, 0, 0]
        self.position = PoseStamped()
        self.publisher1 = self.create_publisher(PoseStamped, "/vicon/Tello_1/Tello_1", 10)
        self.publisher2 = self.create_publisher(PoseStamped, "/vicon/Tello_2/Tello_2", 10)

        self.timer = self.create_timer(self.frequency, self.send_position1)
        self.timer = self.create_timer(self.frequency, self.send_position2)

    def random_position(self):
        self.pose[0] = self.pose[0] + np.random.uniform(-0.05, 0.05)
        self.pose[1] = self.pose[1] + np.random.uniform(-0.05, 0.05)
        self.pose[2] = self.pose[2] + np.random.uniform(-0.05, 0.05)

        position = Point(
            x=self.pose[0],
            y=self.pose[1],
            z=self.pose[2]
        )
        orientation = Quaternion(
            x=0.0,
            y=0.0,
            z=0.0,
            w=1.0
        )
        return position, orientation
    
    def send_position1(self):
        pose, orien = self.random_position()
        self.position.header = Header()
        self.position.header.stamp = self.get_clock().now().to_msg()
        self.position.header.frame_id = 'map'
        self.position.pose.position = pose
        self.position.pose.orientation = orien

        self.get_logger().info("Random position sent")
        self.publisher1.publish(self.position)

    def send_position2(self):
        pose, orien = self.random_position()
        self.position.header = Header()
        self.position.header.stamp = self.get_clock().now().to_msg()
        self.position.header.frame_id = 'map'
        self.position.pose.position = pose
        self.position.pose.orientation = orien

        self.get_logger().info("Random position sent")
        self.publisher2.publish(self.position)


def main():
    rclpy.init()
    node = TestNode(0.1)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()