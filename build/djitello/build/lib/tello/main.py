from djitellopy import Tello
from tello.tello_node import TelloNode
from tello.controller_node import SwarmNode
import rclpy
import threading


FILE_PATH = "/ws/src/djitello/resource/ips.txt"

def main():
    rclpy.init()
    tello_nodes = [TelloNode(Tello("192.168.16.112"), "1"), TelloNode(Tello("192.168.16.113"), "2")]
    for node in tello_nodes:
        threading.Thread(target=rclpy.spin, args=[node], daemon=True).start()
    controller = SwarmNode()
    threading.Thread(target=rclpy.spin, args=(controller,)).start()
    controller.takeoff_and_land()
    rclpy.shutdown()


    





 

