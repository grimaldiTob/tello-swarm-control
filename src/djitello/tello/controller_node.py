from rclpy.node import Node
from std_msgs.msg import String
from custom_msgs.msg import TelloStatus
import time
import rclpy
from geometry_msgs.msg import Pose, PoseStamped

class SwarmNode(Node):

    def __init__(self):
        super().__init__("Controller")
        self.get_logger().info("Controller Initialized!")

        self.positions = []
        self.targets = []

        # Init publishers and subscribers
        self.init_publishers()
        self.init_subscribers()

    def init_subscribers(self):
        self.sub1 = self.create_subscription(TelloStatus, "/Tello1/pose", self.check_position, 10)
        self.sub2 = self.create_subscription(TelloStatus, "/Tello2/pose", self.check_position, 10)

    def init_publishers(self):
        self.publ1 = self.create_publisher(String, "/tello1/cmd", 10)
        self.publ2 = self.create_publisher(String, "/tello2/cmd", 10)

    def check_position(self, msg:TelloStatus):
        position = msg.stamped
        id = msg.id
        self.get_logger().info(f"Posizione x tello {id}: {position.pose.position.x}")
        self.get_logger().info(f"Posizione y tello {id}: {position.pose.position.y}")
        if id == 1:
            if(position.pose.position.x>=1.5 or position.pose.position.y>=1.5):
                self.send_to_publisher_n1("stop")
            else:
                self.send_to_publisher_n1("rc 0 10 0 0")
        elif id == 2:
            if(position.pose.position.x>=1.5 or position.pose.position.y>=1.5):
                self.send_to_publisher_n2("stop")
            else:
                self.send_to_publisher_n2("rc 0 10 0 0")


    def check_position2(self, msg:PoseStamped):
        x = msg.pose.position.x
        y = msg.pose.position.y
        self.get_logger().info(f"Posizione x tello 2: {x}")
        self.get_logger().info(f"Posizione y tello 2: {y}")
        if(x>=1.5 or y>=1.5):
            self.send_to_publisher_n2("stop")
        else:
            self.send_to_publisher_n2("rc 0 -10 0 0")

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
    time.sleep(0.2)
    node = SwarmNode()
    #node.takeoff_and_land(15)
    rclpy.spin(node)
    rclpy.shutdown()

""" def publish_data(self, msg:PoseStamped):
        print(f"Received x: {msg.pose.position.x}")
        self.get_logger().info(f"Received x position: {msg.pose.position.x}")
        self.get_logger().info(f"Received y position: {msg.pose.position.y}")
        self.get_logger().info(f"Received z position: {msg.pose.position.z}")
        self.get_logger().info(f"Received x orientation: {msg.pose.orientation.x}")
        self.get_logger().info(f"Received y orientation: {msg.pose.orientation.y}")
        self.get_logger().info(f"Received z orientation: {msg.pose.orientation.z}")
        self.get_logger().info(f"Received w orientation: {msg.pose.orientation.w}")
        fixed_msg = PoseStamped()
        fixed_msg.header = msg.header
        fixed_msg.pose.position.x = msg.pose.position.x * 2
        fixed_msg.pose.position.y = msg.pose.position.y * 2
        fixed_msg.pose.position.z = msg.pose.position.z * 2
        fixed_msg.pose.orientation = msg.pose.orientation
        self.publ2.publish(msg)"""