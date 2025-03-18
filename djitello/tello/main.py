from djitellopy import Tello
from tello.tello_node import TelloNode
from tello.controller_node import SwarmNode
import rclpy

FILE_PATH = "/ws/src/djitello/resource/ips.txt"

#swarm = TelloSwarm.fromFile(FILE_PATH)

def main():
    rclpy.init()
    tello_nodes = [TelloNode(Tello("192.168.16.112"), "1"), TelloNode(Tello("192.168.16.113"), "2")]
    n = len(tello_nodes)
    rclpy.spin_once(tello_nodes[0])
    rclpy.spin_once(tello_nodes[1])
    controller = SwarmNode()
    #controller.init_publishers(n)
    #rclpy.spin(controller)
    rclpy.shutdown()

 

