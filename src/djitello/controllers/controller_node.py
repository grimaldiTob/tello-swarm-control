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
        self.positions_filtered = [[0, 0, 0],[0, 0, 0]]
        self.observer_pose = [0, 0, 1, 0] # valori di default
        self.quaternion = [0, 0, 0, 1] #quaternion of the observer object
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
        self.aruco_sub = self.create_subscription(PoseStamped, "/vicon/aruco42/aruco42", self.move_observer_pose, 10)

    def init_publishers(self):
        self.publ1 = self.create_publisher(Point, "/tello1/target", 10)
        self.publ2 = self.create_publisher(Point, "/tello2/target", 10)
        self.observer_publ = self.create_publisher(TelloStatus, "/observer/pose", 10)

    def init_service(self):
        self.service = self.create_service(SetPoint, "/controller/setPoint", self.get_observer_pose)

    def init_broadcasters(self):
        self.w_broadcaster = TransformBroadcaster(self) # broadcaster world/observer

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
        t.child_frame_id = 'observer'
        t.transform.translation.x = float(self.observer_pose[0])
        t.transform.translation.y = float(self.observer_pose[1])
        t.transform.translation.z = float(self.observer_pose[2])
        
        self.quaternion_from_euler(0, 0, self.observer_pose[3]) # interessa solo la yaw
        t.transform.rotation.x = float(self.quaternion[1])
        t.transform.rotation.y = self.quaternion[2]
        t.transform.rotation.z = self.quaternion[3]
        t.transform.rotation.w = self.quaternion[0]

        self.w_broadcaster.sendTransform(t)


    def get_observer_pose(self, request, response):
        self.observer_pose[0] = request.x
        self.observer_pose[1] = request.y
        self.observer_pose[2] = request.z
        self.observer_pose[3] = request.yaw
        self.send_observer_pose()
        self.degrees_to_radians()
        self.send_transform()
        self.transform_flag = True
        response.code = True
        return response

    def move_observer_pose(self, msg: PoseStamped):
        if(abs(msg.pose.position.x) < 2 and abs(msg.pose.position.y) < 2):
            self.observer_pose[0] = msg.pose.position.x
            self.observer_pose[1] = msg.pose.position.y
            self.observer_pose[2] = msg.pose.position.z
            self.quaternion = [msg.pose.orientation.x,
                                 msg.pose.orientation.y,
                                 msg.pose.orientation.z,
                                 msg.pose.orientation.w]
            
            euler = self.quaternion_to_euler()
            yaw = euler[0]
            self.observer_pose[3] = yaw * 180 / (math.pi)

            self.send_observer_pose()
            self.degrees_to_radians()

            self.send_transform()
            self.transform_flag = True
        
    def send_observer_pose(self):
        status = TelloStatus()
        status.x = self.observer_pose[0]
        status.y = self.observer_pose[1]
        status.z = self.observer_pose[2]
        status.id = int(self.observer_pose[3])
        self.observer_publ.publish(status)

    def check_position(self, msg:TelloStatus):
        position = [msg.x, msg.y, msg.z]
        id = int(msg.id)
        self.positions[id-1] = position #perché gli id sono numerati da 1 piuttosto che da 0 come le liste

    def setup_staticBroadcasters(self):
        self.closest_drone(0)
        self.get_logger().info(f"Closest drone is {self.idx_closest}")
        st = TransformStamped()
        now = self.get_clock().now().to_msg()
        st.header.stamp = now
        st.header.frame_id = 'observer'
        st.child_frame_id = 'observer_offset'

        st.transform.translation.x = 1.0
        st.transform.translation.y = 0.0
        st.transform.translation.z = 0.0

        st.transform.rotation.x = 0.0
        st.transform.rotation.y = 0.0
        st.transform.rotation.z = 0.0
        st.transform.rotation.w = 1.0

        st2 = TransformStamped()
        st2.header.stamp = now
        st2.header.frame_id = 'observer_offset'
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
        self.closest_drone(0.6)
        if self.transform_flag:
            try:
                now = rclpy.time.Time()
                trans1 = self.tf_buffer.lookup_transform('world', 'observer_offset', now)

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

            

    def closest_drone(self, alpha):
        # calcolo dell'indice del drone più vicino all' observer
        observer_pose = np.array(self.observer_pose[:3])  # Prendo x, y e z
        distances = []
        for i, position in enumerate(self.positions):
            position_filtered = np.array(self.positions_filtered[i])
            np_position = np.array(position)
            self.positions_filtered[i] = position_filtered*alpha + np_position*(1-alpha)
            distance = np.linalg.norm(self.positions_filtered[i] - observer_pose)
            distances.append(distance)
        self.idx_closest = np.argmin(distances)

    def vision(self):
        dx = self.positions[self.idx_closest][0] - self.observer_pose[0]
        dy = self.positions[self.idx_closest][1] - self.observer_pose[1]
        distance = math.sqrt(dx**2 + dy**2)

        self.get_logger().info(f"Distance: {distance}")
        if distance > 1.30:
            return False
        
        angle_to_drone = math.atan2(dy, dx)
        yaw = self.observer_pose[3] 

        angle_diff = math.atan2(math.sin(angle_to_drone - yaw), math.cos(angle_to_drone - yaw))
        self.get_logger().info(f"Angle Diff: {angle_diff}")
        fov = math.radians(45)
        self.get_logger().info(f"{angle_diff} and {fov}")
        if abs(angle_diff) <= fov:
            self.get_logger().info("I droni sono visibili!")
            return True
        return False
    
    def t1_publisher(self, target):
        point = Point()
        self.get_logger().info(f"{target}")
        point.x = target[0]
        point.y = target[1]
        point.z = target[2]
        self.publ1.publish(point)

    def t2_publisher(self, target):
        point = Point()
        point.x = target[0]
        point.y = target[1]
        point.z = target[2]
        self.publ2.publish(point)

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
        self.observer_pose[3] = self.observer_pose[3] * np.pi / 180

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
