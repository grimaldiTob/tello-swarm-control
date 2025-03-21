from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import String
import time
import rclpy

# nodo di controllo, invia i comandi ai singoli nodi
class SwarmNode(Node):

    def __init__(self):
        super().__init__("Controller")
        self.get_logger().info("Swarm Initialized!")
        self.publ1 = self.create_publisher(String, "/Command/tello1", 10)
        self.publ2 = self.create_publisher(String, "/Command/tello2", 10)

    def send_to_publisher_n1(self, command: str):
        msg = String()
        msg.data = command
        self.publ1.publish(msg)
        self.get_logger().info(f"Sent command: {command}")

    def send_to_publisher_n2(self, command: str):
        msg = String()
        msg.data = command
        self.publ2.publish(msg)
        self.get_logger().info(f"Sent command: {command}")

    def takeoff_and_land(self, delay: float = 10.0):
        self.send_to_publisher_n1("takeoff")
        self.send_to_publisher_n2("takeoff")
        self.get_logger().info(f"Waiting {delay} seconds before landing...")
        time.sleep(delay)
        self.send_to_publisher_n1("land")
        self.send_to_publisher_n2("land")

def main():
    rclpy.init()
    node = SwarmNode()
    while rclpy.ok():
        rclpy.spin_once(node)
    rclpy.shutdown()
