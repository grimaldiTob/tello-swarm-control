from djitellopy import Tello, TelloSwarm, TelloException
import rclpy
from rclpy import Node
from std_msgs.msg import String

PATH_FILE = "resource/ips.txt"

class SwarmNode(Node):

    def __init__(self):
        super().__init__()
        self.get_logger().info(f"Inizializzando lo swarm")
        self.publisher1 = self.create_publisher(String, "/cmd/tello1", 10)
        self.publisher2 = self.create_publisher(String, "/cmd/tello2", 10)


def main(args=None):
    rclpy.init(args=args)
    node = SwarmNode()
    rclpy.spin(node)
    rclpy.shutdown()