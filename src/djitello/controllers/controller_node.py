from rclpy.node import Node
from geometry_msgs.msg import Point, TransformStamped
from custom_msgs.msg import TelloStatus
from custom_msgs.srv import SetPoint
from geometry_msgs.msg import PoseStamped
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster, Buffer, TransformListener

import time
import numpy as np
import rclpy
import math

class SwarmNode(Node):

    def __init__(self):
        super().__init__("Controller")
        self.get_logger().info("Controller Initialized!")

        self.positions = [[0, 0, 0], [0, 0, 0]]
        self.setpoint = [0, 0, 1, 0] # valori di default
        self.quaternion = [0, 0, 0, 1] #quaternion of the setpoint object
        self.timer = 0
        self.idx_closest = 0
        self.transform_flag = False # settata a False finché non sono istanziate le trasformate


        # Init publishers, subscribers and broadcasters
        self.init_publishers()
        self.init_subscribers()
        self.init_service()
        self.init_broadcasters()
        self.init_listeners()

        self.timer = self.create_timer(0.1, self.send_targets)

    def init_subscribers(self):
        self.sub = self.create_subscription(TelloStatus, "/Tello/pose", self.check_position, 10)
        self.aruco_sub = self.create_subscription(PoseStamped, "/vicon/aruco42/aruco42", self.move_setPoint, 10)

    def init_publishers(self):
        self.publ1 = self.create_publisher(Point, "/tello1/target", 10)
        self.publ2 = self.create_publisher(Point, "/tello2/target", 10)
        self.setPoint_publ = self.create_publisher(TelloStatus, "/setpoint/pose", 10)

    def init_service(self):
        self.service = self.create_service(SetPoint, "/controller/setPoint", self.get_setPoint)

    def init_broadcasters(self):
        self.w_broadcaster = TransformBroadcaster(self) # broadcaster world/setpoint

        self.send_transform()
        
        # istanzio lo static broadcaster
        self.s_broadcaster = StaticTransformBroadcaster(self)
        self.setup_staticBroadcasters()
    
    def init_listeners(self):
        # istanzio il listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def send_transform(self):
        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'setpoint'
        t.transform.translation.x = float(self.setpoint[0])
        t.transform.translation.y = float(self.setpoint[1])
        t.transform.translation.z = float(self.setpoint[2])
        
        self.quaternion_from_euler(0, 0, self.setpoint[3]) # interessa solo la yaw
        t.transform.rotation.x = self.quaternion[1]
        t.transform.rotation.y = self.quaternion[2]
        t.transform.rotation.z = self.quaternion[3]
        t.transform.rotation.w = self.quaternion[0]

        self.w_broadcaster.sendTransform(t)


    def get_setPoint(self, request, response):
        self.setpoint[0] = request.x
        self.setpoint[1] = request.y
        self.setpoint[2] = request.z
        self.setpoint[3] = request.yaw
        self.send_setPoint()
        self.degrees_to_radians()
        self.send_transform()
        self.transform_flag = True
        #self.get_logger().info("Set new target")
        #self.compute_target()
        response.code = True
        return response

    def move_setPoint(self, msg: PoseStamped):
        if(abs(msg.pose.position.x) < 2 and abs(msg.pose.position.y) < 2):
            self.setpoint[0] = msg.pose.orientation.x
            self.setpoint[1] = msg.pose.position.y
            self.setpoint[2] = msg.pose.position.z
            self.quaternion = [msg.pose.orientation.x,
                                 msg.pose.orientation.y,
                                 msg.pose.orientation.z,
                                 msg.pose.orientation.w]
            
            euler = self.quaternion_to_euler()
            yaw = euler[0]
            self.get_logger().info(f"Posizione del setpoint ricevuta con yaw {yaw}")
            self.setpoint[3] = yaw * 180 / (math.pi)

            self.send_setPoint()
            self.degrees_to_radians()

            self.send_transform()
            self.transform_flag = True
        
    def send_setPoint(self):
        status = TelloStatus()
        status.x = self.setpoint[0]
        status.y = self.setpoint[1]
        status.z = self.setpoint[2]
        status.id = int(self.setpoint[3])
        self.setPoint_publ.publish(status)

    def check_position(self, msg:TelloStatus):
        position = [msg.x, msg.y, msg.z]
        self.get_logger().info(f"Received position {position}")
        id = int(msg.id)
        self.positions[id-1] = position #perché gli id sono numerati da 1 piuttosto che da 0 come le liste

    def setup_staticBroadcasters(self):
        self.closest_drone()
        self.get_logger().info(f"Closest drone is {self.idx_closest}")
        st = TransformStamped()
        now = self.get_clock().now().to_msg()
        st.header.stamp = now
        st.header.frame_id = 'setpoint'
        st.child_frame_id = 'setpoint_offset'

        st.transform.translation.x = 1.0
        st.transform.translation.y = 0.0
        st.transform.translation.z = 0.0

        st.transform.rotation.x = 0.0
        st.transform.rotation.y = 0.0
        st.transform.rotation.z = 0.0
        st.transform.rotation.w = 1.0

        st2 = TransformStamped()
        st2.header.stamp = now
        st2.header.frame_id = 'setpoint_offset' #'tello' + str(self.idx_closest + 1)
        st2.child_frame_id = 'drone_offset'

        st2.transform.translation.x = 0.75
        st2.transform.translation.y = 0.0
        st2.transform.translation.z = 0.0

        st2.transform.rotation.x = 0.0
        st2.transform.rotation.y = 0.0
        st2.transform.rotation.z = 0.0
        st2.transform.rotation.w = 1.0
        self.s_broadcaster.sendTransform([st, st2])

    def send_targets(self):
        if self.transform_flag:
            try:
                now = rclpy.time.Time()
                trans1 = self.tf_buffer.lookup_transform('world', 'setpoint_offset', now)

                closest_target = []
                closest_target.append(trans1.transform.translation.x)
                closest_target.append(trans1.transform.translation.y)
                closest_target.append(trans1.transform.translation.z)

                trans2 = self.tf_buffer.lookup_transform('world', 'drone_offset', now)

                furthest_target = []
                furthest_target.append(trans2.transform.translation.x)
                furthest_target.append(trans2.transform.translation.y)
                furthest_target.append(trans2.transform.translation.z)

                if self.vision():
                    if self.idx_closest == 0:
                        self.t1_publisher(closest_target)
                        self.t2_publisher(furthest_target)
                    else:
                        self.t2_publisher(closest_target)
                        self.t1_publisher(furthest_target)
                else:
                    self.t1_publisher(self.positions[0])
                    self.t2_publisher(self.positions[1])
            except Exception as e:
                self.get_logger().warn(f'Could not transform to world frame: {e}')

            

    def closest_drone(self):
        # calcolo dell'indice del drone più vicino al setpoint
        setPoint = np.array(self.setpoint[:3])  # Prendiamo x, y e z
        distances = []
        for position in self.positions:
            #position_filtered = position_filtered*alpha + position*(1-alpha)
            distance = np.linalg.norm(position - setPoint)
            distances.append(distance)
        self.idx_closest = np.argmin(distances)

    def vision(self):
        dx = self.positions[self.idx_closest][0] - self.setpoint[0]
        dy = self.positions[self.idx_closest][1] - self.setpoint[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 1.0:
            return False
        
        angle_to_drone = math.atan2(dy, dx)
        yaw = self.setpoint[3] 

        angle_diff = math.atan2(math.sin(angle_to_drone - yaw), math.cos(angle_to_drone - yaw))

        fov = math.radians(30)
        self.get_logger().info(f"{angle_diff} and {fov}")
        if abs(angle_diff) <= fov:
            self.get_logger().info("I droni sono visibili!")
            return True
        return False



    def compute_target(self):
        """
        Funzione che calcola quale drone è piu vicino al set point e il suo punto più vicino alla retta passante per il set point
        In seguito si ricava il secondo target prolungando la proiezione di 30 cm e passando il target in base all'indice ricavato
        """
        time.sleep(0.1)
        setPoint = np.array(self.setpoint[:3])  # Prendiamo x, y e z
        yaw = self.setpoint[3] # Prendiamo la yaw  del setpoint

        # Calcola il versore nel piano xy
        direction = np.array([np.cos(yaw), np.sin(yaw), 0])

        self.closest_drone()
        closest_drone = self.positions[self.idx_closest] # drone più vicino al setPoint

        vector_to_drone = closest_drone - setPoint
        projection = np.dot(vector_to_drone, direction) # lunghezza della proiezione sulla retta

        # Calcola punto sulla retta più vicino al drone
        target_closest = setPoint + projection * direction
        target_furthest = setPoint + (projection + 0.50) * direction # considero la proiezione 50 cm più lunga e calcolo il secondo target
        if self.idx_closest == 0:
            self.t1_publisher(target_closest.tolist())
            self.t2_publisher(target_furthest.tolist())
        else:
            self.t2_publisher(target_closest.tolist())
            self.t1_publisher(target_furthest.tolist())
    
    def t1_publisher(self, target):
        point = Point()
        self.get_logger().info(f"{target}")
        point.x = target[0]
        point.y = target[1]
        point.z = target[2]
        self.publ1.publish(point)
        self.get_logger().info(f"Sent point: {point}")

    def t2_publisher(self, target):
        point = Point()
        point.x = target[0]
        point.y = target[1]
        point.z = target[2]
        self.publ2.publish(point)
        self.get_logger().info(f"Sent point: {point}")

    def quaternion_to_euler(self):
        (x, y, z, w) = self.quaternion
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
    
    def degrees_to_radians(self):
        self.setpoint[3] = self.setpoint[3] * np.pi / 180

    def quaternion_from_euler(self, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        self.quaternion[0] = cy * cp * cr + sy * sp * sr
        self.quaternion[1] = cy * cp * sr - sy * sp * cr
        self.quaternion[2] = sy * cp * sr + cy * sp * cr
        self.quaternion[3] = sy * cp * cr - cy * sp * sr


def main():
    rclpy.init()
    time.sleep(0.2)
    node = SwarmNode()
    rclpy.spin(node)
    rclpy.shutdown()
