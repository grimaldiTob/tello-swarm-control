from djitellopy import TelloSwarm
from tello_node import TelloNode
from controller_node import SwarmNode
import rclpy

FILE_PATH = "resource/ips.txt"

swarm = TelloSwarm.fromFile(FILE_PATH)

# lista di nodi tello
tello_nodes = []

def main():
    for i in enumerate(swarm.tellos):
        tello_nodes[i] = TelloNode(swarm.tellos[i], str(i+1))
    n = len(swarm.tellos)
    controller = SwarmNode()
    controller.init_publishers(n)

 

