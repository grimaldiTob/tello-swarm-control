from djitellopy import Tello
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from custom_msgs.srv import StringCommand
import rclpy


class TelloNode(Node):

    def __init__(self):
        super().__init__("tello")
        self.declare_parameter("tello_ip", "192.168.16.112")
        self.declare_parameter("id", "0")
        self.tello = Tello(self.get_parameter("tello_ip").value)
        self.ip = self.get_parameter('tello_ip').value
        self.id = self.get_parameter("id").value
        self.get_logger().info(f"Tello initialized with IP address: {self.tello.address[0]}")
        self.srv = self.create_service(StringCommand, "/tello" + self.id, self.srv_command)
        self.controller_cmd = self.create_subscription(String, "/Command/tello" + self.id, self.ctrl_command, 10)
        self.viconState = self.create_subscription(Pose, "/viconState/tello" + self.id, self.callback, 10)
        #self.tello.connect()

    def callback(self):
        return
    
    def ctrl_command(self, msg: String):
        #self.tello.send_control_command(msg.data)
        self.get_logger().info(f"Received command by the tello: {msg.data}")
    
    def srv_command(self, request, response):
        #self.tello.send_control_command(request.command)
        self.get_logger().info(f"Received command by the tello: {request.command}")
        response.code = True
        return response


def main():
    rclpy.init()
    node = TelloNode()
    #while rclpy.ok():
    #   rclpy.spin_once(node)
    rclpy.spin(node)
    rclpy.shutdown()




