from djitellopy import Tello, TelloException
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
from geometry_msgs.msg import Point, PoseStamped, TransformStamped
from custom_msgs.srv import StringCommand, Variance, SetPoint
from custom_msgs.msg import TelloStatus
from tf2_ros import TransformBroadcaster
from std_srvs.srv import Trigger
from controllers.PID_controller import PIDController
import math
import time
import numpy as np


class TelloNode(Node):

    def __init__(self, ip:str, id:int):
        super().__init__("tello" + str(id))

        #parameters
        self.ip = ip
        self.id = str(id)
        self.tello_pose = [0, 0, 0]
        self.tello_quaternion = [0, 0, 0, 0] # valori di default
        self.target = [-1, -1, 1, 0]
        self.setpoint = [0, 0, 0, 0] #(x,y,z, yaw) del setpoint
        self.variance = 0 # varianza di default settata a 0
        self.frequency = 6
        self.lastReceived = 0

        self.broadcaster = TransformBroadcaster(self) # broadcaster world/tello

        #setup Tello
        self.tello = Tello(self.ip)
        self.get_logger().info(f"Tello initialized with IP address: {self.tello.address[0]} \nid: {self.id}")

        #Setup ROS2 workspace
        self.setup_services()
        self.setup_subscribers()
        self.setup_publishers()

        #Setup PID controllers
        self.setup_PID()

        self.tello.connect()
        self.timer = self.create_timer(1/self.frequency, self.elaborate_position)
        self.timer_ = self.create_timer(1/self.frequency, self.send_status)
        self.publish_timer = self.create_timer(1, self.log_data)

    def setup_publishers(self):
        self.status_publisher = self.create_publisher(TelloStatus, "/Tello/pose", 10)
        self.error_publisher = self.create_publisher(TelloStatus, "/Tello/error", 10)
    
    def setup_subscribers(self):
        self.controller_cmd = self.create_subscription(Point, "/tello" + self.id + "/target", self.target_change, 10)
        self.viconState = self.create_subscription(PoseStamped, "/vicon/Tello_" + self.id + "/Tello_" + self.id, self.set_pose, 10)
        self.setPoint_pose = self.create_subscription(TelloStatus, "/setpoint/pose", self.change_setPoint, 10)

    def setup_services(self):
        self.cmd_srv = self.create_service(StringCommand, "/tello" + self.id, self.srv_command)
        self.tkf_srv = self.create_service(Trigger, "/tello" + self.id + "/takeoff", self.takeoff_srv)
        self.lnd_srv = self.create_service(Trigger, "/tello" + self.id + "/land", self.land_srv)
        self.var_srv = self.create_service(Variance, "/tello" + self.id + "/variance", self.set_variance)
        self.tar_srv = self.create_service(SetPoint, "/tello" + self.id + "/target", self.set_target)

    def setup_PID(self):
        self.PIDx = PIDController('x')
        self.PIDy = PIDController('y')
        self.PIDz = PIDController('z')
        self.PIDyaw = PIDController('yaw')
        self.PIDx.set_PID_safeopt([0.55, 0, 0.20])
        self.PIDy.set_PID_safeopt([0.55, 0, 0.20])
        self.PIDz.set_PID_safeopt([0.55, 0, 0.35])
        self.PIDyaw.set_PID_safeopt([0.90, 0.0, 0.08])

    def set_pose(self, msg:PoseStamped):
        # setting the tello pose received by the vicon
        self.tello_pose = [msg.pose.position.x,
                           msg.pose.position.y,
                           msg.pose.position.z]
        self.tello_quaternion = [msg.pose.orientation.x,
                                 msg.pose.orientation.y,
                                 msg.pose.orientation.z,
                                 msg.pose.orientation.w]
        self.lastReceived = time.time()

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'tello' + self.id

        t.transform.translation.x = msg.pose.position.x
        t.transform.translation.y = msg.pose.position.y
        t.transform.translation.z = msg.pose.position.z

        t.transform.rotation = msg.pose.orientation

        self.broadcaster.sendTransform(t)
        
    def send_status(self):
        # creating the Status object
        status = TelloStatus()
        meas = np.array(self.tello_pose)
        noise_pos= self.add_gaussian_noise(meas)
        #self.get_logger().info(f"Received for {meas.tolist()} noise values {noise_pos.tolist()}")
        noise_pos = meas + noise_pos
        status.x = noise_pos[0]
        status.y = noise_pos[1]
        status.z = noise_pos[2]
        status.id = int(self.id)
        self.status_publisher.publish(status) #publish status  

    def target_change(self, msg: Point):
        self.target[0] = msg.x
        self.target[1] = msg.y
        self.target[2] = msg.z

    
    def elaborate_position(self):
        euler = self.tello.get_yaw()
        yaw_d = -euler
        yaw = yaw_d*(math.pi)/180      
        target_yaw = calculate_yaw((self.setpoint[0] - self.tello_pose[0]), (self.setpoint[1] - self.tello_pose[1]), degrees=True)# calcolo della yaw target in gradi
        self.get_logger().info(f"Yaw: {yaw_d}\nSetpoint jaw: {self.setpoint[3]}\nTarget yaw: {target_yaw}")
        if self.tello.is_flying:
            #calculating errors
            error_x = float(((self.target[0]-self.tello_pose[0])*math.cos(yaw) + (self.target[1]-self.tello_pose[1])*math.sin(yaw))*100)
            error_y = float((-(self.target[0]-self.tello_pose[0])*math.sin(yaw) + (self.target[1]-self.tello_pose[1])*math.cos(yaw))*100)
            error_z = float((self.target[2] - self.tello_pose[2])*100)
            self.publish_error(error_x, error_y, error_z)
            error_yaw = float(target_yaw-yaw_d)

            # compute action
            action_x = int(self.PIDx.compute_action(error_x)/1.5)
            action_y = -int(self.PIDy.compute_action(error_y)/1.5)
            action_z = int(self.PIDz.compute_action(error_z)/1.5)
            action_yaw = -int(self.PIDyaw.compute_action(error_yaw)*1.5)

            if abs(action_x) < 3 and abs(action_y) < 3 and abs(action_z) < 3:
                action_x, action_y, action_z = 0, 0, 0
                self.get_logger().info("On the target!!!")


            if (time.time()-self.lastReceived) > (2/self.frequency):
                action_x, action_y, action_z = 0, 0, 0
                self.get_logger().info("Vicon Timeout!!!")
            
            self.get_logger().info(f"Rc command: {action_y}, {action_x}, {action_z}, {action_yaw}")
            self.tello.send_rc_control(action_y,action_x, action_z, action_yaw)

    def change_setPoint(self, msg: TelloStatus):
        self.setpoint[0] = msg.x
        self.setpoint[1] = msg.y
        self.setpoint[2] = msg.z
        self.setpoint[3] = msg.id
    
    def srv_command(self, request, response):
        try:
            self.get_logger().info(f"Received command by the tello{self.id}: {request.command}")
            self.tello.send_control_command(request.command)
            response.code = True
        except TelloException:
            self.get_logger().info(f"Error received by the tello{self.id}")
            response.code = False
        return response
    
    def takeoff_srv(self, request, response):
        try:
            self.tello.takeoff()
            self.tello.is_flying = True
            response.success = True
            response.message = "Takeoff started!"
        except TelloException:
            response.success = False
            response.message = "Decollo aborted!"
        return response

    def land_srv(self, request, response):
        self.tello.send_rc_control("rc 0 0 0 0")
        self.tello.land()
        self.tello.is_flying = False
        response.success = True
        response.message = "Landing..."
        return response
    
    def set_variance(self, request, response):
        var = request.variance
        self.variance = var
        response.data =  True
        return response
    
    def set_target(self, request, response):
        self.target[0] = request.x
        self.target[1] = request.y
        self.target[2] = request.z
        response.code = True
        return response
     

    def battery_check(self):
        bat = int(self.tello.get_battery())
        time.sleep(0.1)
        if bat > 10:
            self.get_logger().info(f"Battery is at {bat}%")
            return True
        else:
            self.get_logger().info(f"Battery is too low. Recharge")
            return False
    
    def log_data(self):
        self.get_logger().info(f"Posizione tello {self.tello_pose}")
        self.get_logger().info(f"Target {self.target}")
        
    def publish_error(self, x, y, z):
        error = TelloStatus()
        error.x = x
        error.y = y
        error.z = z
        error.id = int(self.id)
        self.error_publisher.publish(error)
    
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
    
    def add_gaussian_noise(self, measurement):
        std_dev = np.sqrt(self.variance)
        noise = np.random.normal(loc=0.0, scale=std_dev, size=np.shape(measurement))
        return noise

def main():
    rclpy.init()
    node1 = TelloNode("192.168.16.112", 2)
    node2 = TelloNode("192.168.16.113", 1)
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

def calculate_yaw(x, y, degrees=False):
    yaw = math.atan2(y, x)  # atan2 gestisce correttamente tutti i quadranti
    return math.degrees(yaw) if degrees else yaw

