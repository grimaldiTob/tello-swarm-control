from djitellopy import Tello
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, PoseStamped
from custom_msgs.srv import StringCommand
from custom_msgs.msg import TelloStatus
from rclpy.executors import MultiThreadedExecutor
import rclpy
import threading
from controllers.PID_controller import PIDController
import math


class TelloNode(Node):

    def __init__(self, ip:str, id:int):
        super().__init__("tello" + str(id))

        #parameters
        self.ip = ip
        self.id = str(id)
        self.tello_pose = ()
        self.tello_quaternion = ()
        self.target = [0, 0, 0]

        #setup Tello
        self.tello = Tello(self.ip)
        self.get_logger().info(f"Tello initialized with IP address: {self.tello.address[0]} \nid: {self.id}")

        #Setup ROS2 workspace
        self.setup_services()
        self.setup_subscribers()
        self.setup_publishers()

        #Setup PID controllers
        self.setup_PID()

        #self.tello.connect()

    def setup_publishers(self):
        self.status_publisher = self.create_publisher(TelloStatus, "/Tello"+ self.id + "/pose", 10)
    
    def setup_subscribers(self):
        self.controller_cmd = self.create_subscription(String, "/tello" + self.id + "/cmd", self.ctrl_command, 10)
        self.viconState = self.create_subscription(PoseStamped, "/vicon/Tello_" + self.id + "/Tello_" + self.id, self.set_pose, 10)

    def setup_services(self):
        self.srv = self.create_service(StringCommand, "/tello" + self.id, self.srv_command)

    def setup_PID(self):
        self.PIDx = PIDController('x')
        self.PIDy = PIDController('y')
        self.PIDz = PIDController('z')
        self.PIDx.set_PID_safeopt([0.57531093, 0.02, 0.17326167])
        self.PIDy.set_PID_safeopt([0.7, 0.02, 0.27326167])
        self.PIDz.set_PID_safeopt([0.5, 0.02, 0.15])

    def compute_error(self):
        euler = self.quaternion_to_euler()
        yaw = euler[0]
        error_x = float((self.target[0]-self.tello_pose[0])*math.cos(yaw) + (self.target[1]-self.tello_pose[1])*math.sin(yaw))
        error_y = float(-(self.target[0]-self.tello_pose[0])*math.sin(yaw) + (self.target[1]-self.tello_pose[1])*math.cos(yaw))
        error_z = float(self.target[2] - self.tello_pose[2])
        error_yaw = float(-yaw)
        self.tello.send_rc_control(error_x, error_y, error_z, error_yaw)

    def set_pose(self, msg:PoseStamped):
        # setting the tello pose received by the vicon
        self.tello_pose = (msg.pose.position.x,
                           msg.pose.position.y,
                           msg.pose.position.z)
        self.tello_quaternion = (msg.pose.orientation.x,
                                 msg.pose.orientation.y,
                                 msg.pose.orientation.z,
                                 msg.pose.orientation.w)

        # creating the Status object
        status = TelloStatus()
        status.stamped = msg
        status.id = self.id
        self.status_publisher.publish(status) #publish status

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

    def quaternion_to_euler(self):
        (x, y, z, w) = self.tello_quaternion
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(t0, t1)
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.asin(t2)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(t3, t4)
        return [yaw, pitch, roll]

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




