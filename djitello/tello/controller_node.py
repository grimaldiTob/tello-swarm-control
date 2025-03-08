import rclpy
from rclpy import Node
from std_msgs.msg import String

# nodo di controllo, invia i comandi ai singoli nodi
class SwarmNode(Node):

    def __init__(self):
        super().__init__()
        self.get_logger().info(f"Inizializzando lo swarm")
        self.publishers = [] # lista vuota di publishers

    # creo i publisher in base agli n tello nello swarm
    def init_publishers(self, n:int):
        for i in range(n):
            self.publishers[i] = self.create_publisher(String, "/Command/tello" + i, 10)
