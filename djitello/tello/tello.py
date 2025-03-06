from djitellopy import Tello
import rclpy
from rclpy import Node
from std_msgs.msg import String

FILE_PATH = "resource/ips.txt"

class TelloNode(Node):

    def __init__(self, tello:Tello):
        super().__init__()
        self.tello = tello
        self.get_logger().info(f"Inizializzato il tello con address: {self.tello.address[0]}")
        self.publisher_ = self.create_publisher(String, "/State/noise", 10)
        self.subscriber = self.create_subscription(String, "/State/noise", 10)

with open(FILE_PATH, "r") as f:
    ip_lines = f.readlines()

def main(args=None):
    rclpy.init(args=args)
    node = TelloNode(Tello())
    rclpy.spin(node)
    rclpy.shutdown()