from rclpy.node import Node
from std_msgs.msg import String

# nodo di controllo, invia i comandi ai singoli nodi
class SwarmNode(Node):

    def __init__(self):
        super().__init__("Controller")
        self.get_logger().info("Inizializzando lo swarm")
        self.publisher_ = []

    # creo i publisher in base agli n tello nello swarm
    def init_publishers(self, n:int):
        for i in range(n):
            #self.publisher_[i] = self.create_publisher(String, "/Command/tello" + str(i), 10)
            self.get_logger().info("Creato pubblisher al topic /Command/tello " + str(i))
