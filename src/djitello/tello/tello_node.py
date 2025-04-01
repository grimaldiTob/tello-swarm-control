from djitellopy import Tello
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, PoseStamped
from custom_msgs.srv import StringCommand
from custom_msgs.msg import TelloStatus
from rclpy.executors import MultiThreadedExecutor
import rclpy
import threading


class TelloNode(Node):

    def __init__(self, ip:str, id:int):
        super().__init__("tello" + str(id))

        #parameters
        self.ip = ip
        self.id = str(id)
        self.tello_pose = PoseStamped()

        self.tello = Tello(self.ip)
        self.get_logger().info(f"Tello initialized with IP address: {self.tello.address[0]} \nid: {self.id}")

        #Setup ROS2 workspace
        self.setup_services()
        self.setup_subscribers()
        self.setup_publishers()

        #self.tello.connect()

    def setup_publishers(self):
        self.status_publisher = self.create_publisher(TelloStatus, "/Tello"+ self.id + "/pose", 10)
    
    def setup_subscribers(self):
        self.controller_cmd = self.create_subscription(String, "/tello" + self.id + "/cmd", self.ctrl_command, 10)
        self.viconState = self.create_subscription(PoseStamped, "/vicon/Tello_" + self.id + "/Tello_" + self.id, self.set_pose, 10)

    def setup_services(self):
        self.srv = self.create_service(StringCommand, "/tello" + self.id, self.srv_command)

    def set_pose(self, msg:PoseStamped):
        # setting the tello pose received by the vicon
        self.tello_pose = msg

        # creating the Status object
        status = TelloStatus()
        status.stamped = msg
        status.id = self.id
        self.status_publisher.publish(status) #publish status

    """def callback(self, msg:PoseStamped):
        self.get_logger().info("Ricevuto messaggio dal controller")
        self.get_logger().info(f"Received x position: {msg.pose.position.x}")
        self.get_logger().info(f"Received y position: {msg.pose.position.y}")
        self.get_logger().info(f"Received z position: {msg.pose.position.z}")
        self.get_logger().info(f"Received x orientation: {msg.pose.orientation.x}")
        self.get_logger().info(f"Received y orientation: {msg.pose.orientation.y}")
        self.get_logger().info(f"Received z orientation: {msg.pose.orientation.z}")
        self.get_logger().info(f"Received w orientation: {msg.pose.orientation.w}")"""
    
    def ctrl_command(self, msg: String):
        self.tello.send_control_command(msg.data)
        self.get_logger().info(f"Received command by the tello: {msg.data}")
    
    def srv_command(self, request, response):
        if request.command == "takeoff":
            self.tello.takeoff()
        elif request.command == "land":
            self.tello.land()
        else:
            self.tello.send_control_command(request.command)
        response.code = True
        self.get_logger().info(f"Received command by the tello{self.id}: {request.command}")
        return response


def main():
    rclpy.init()
    node1 = TelloNode("192.168.16.112", 1)
    node2 = TelloNode("192.168.16.113", 2)
    executor = MultiThreadedExecutor()
    executor.add_node(node1)
    executor.add_node(node2)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        node2.destroy_node()
        rclpy.shutdown()


    """rclpy.spin(node1)
    rclpy.spin(node2)
    node1.destroy_node()
    node2.destroy_node()
    rclpy.shutdown()"""




