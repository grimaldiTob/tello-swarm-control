from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
from custom_msgs.msg import TelloStatus
from custom_msgs.msg import setPoint
import time
import numpy as np
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
        position = [msg.x, msg.y, msg.z]
        id = int(msg.id)
        self.positions[id-1] = position #perché gli id sono numerati da 1 piuttosto che da 0 come le liste

    
    def compute_target(self):
        """
        Funzione che calcola quale drone è piu vicino al set point e il suo punto più vicino alla retta passante per il set point

        """
        setPoint = np.array(self.setpoint[:3])  # Prendiamo x, y e z
        yaw = self.setpoint[3] # Prendiamo la yaw  del setpoint

        # 2. Calcola il versore nel piano xy
        direction = np.array([np.cos(yaw), np.sin(yaw), 0])

        distances = np.linalg.norm(self.positions - setPoint, axis=1)
        idx_closest = np.argmin(distances)
        closest_drone = self.positions[idx_closest] # drone più vicino al setPoint

        vector_to_drone = closest_drone - setPoint
        projection = np.dot(vector_to_drone, direction) # lunghezza della proiezione sulla retta

        # 6. Calcola punto sulla retta più vicino al drone
        target_closest = setPoint + projection * direction
        target_furthest = setPoint + (projection + 0.30) * direction # considero la proiezione 30 cm più lunga e calcolo il secondo target
        if idx_closest == 0:
            self.send_to_publisher_n1(target_closest.tolist())
            self.send_to_publisher_n2(target_furthest.tolist())
        else:
            self.send_to_publisher_n2(target_closest.tolist())
            self.send_to_publisher_n1(target_furthest.tolist())



    
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
    
    def degrees_to_radians(self):
        self.setpoint[3] = self.setpoint[3] * np.pi / 180


def main():
    rclpy.init()
    time.sleep(0.2)
    node = SwarmNode()
    rclpy.spin(node)
    rclpy.shutdown()
