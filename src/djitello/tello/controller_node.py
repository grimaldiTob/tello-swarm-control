from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
from custom_msgs.msg import TelloStatus
from custom_msgs.msg import setPoint
import time
import rclpy

class SwarmNode(Node):

    def __init__(self):
        super().__init__("Controller")
        self.get_logger().info("Controller Initialized!")

        self.positions = []
        self.setpoint = ()

        # Init publishers and subscribers
        self.init_publishers()
        self.init_subscribers()
        self.init_service()

    def init_subscribers(self):
        self.sub1 = self.create_subscription(TelloStatus, "/Tello1/pose", self.check_position, 10)
        self.sub2 = self.create_subscription(TelloStatus, "/Tello2/pose", self.check_position, 10)

    def init_publishers(self):
        self.publ1 = self.create_publisher(Point, "/tello1/target", 10)
        self.publ2 = self.create_publisher(Point, "/tello2/target", 10)

    def init_service(self):
        self.service = self.create_service(setPoint, "/controller/setPoint", self.get_setPoint)

    def get_setPoint(self, request, response):
        self.setpoint[0] = request.x
        self.setpoint[1] = request.y
        self.setpoint[2] = request.z
        self.setpoint[3] = request.yaw
        response.code = True
        return response

    def check_position(self, msg:TelloStatus):
        position = msg.stamped
        id = int(msg.id)
        self.get_logger().info(f"Posizione x tello {id}: {position.pose.position.x}")
        self.get_logger().info(f"Posizione y tello {id}: {position.pose.position.y}")
        self.positions[id-1] = position
    
    def send_to_publisher_n1(self, target):
        point = Point()
        point.x = target[0]
        point.y = target[1]
        point.z = target[2]
        self.publ1.publish(point)
        self.get_logger().info(f"Sent point: {point}")

    def send_to_publisher_n2(self, target):
        point = Point()
        point.x = target[0]
        point.y = target[1]
        point.z = target[2]
        self.publ2.publish(point)
        self.get_logger().info(f"Sent point: {point}")

def main():
    rclpy.init()
    time.sleep(0.2)
    node = SwarmNode()
    rclpy.spin(node)
    rclpy.shutdown()
