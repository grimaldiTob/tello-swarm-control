from djitellopy import Tello
import rclpy
from rclpy import Node
from std_msgs.msg import String



class TelloNode(Node):

    def __init__(self, tello:Tello, i:String):
        super().__init__()
        self.tello = tello
        self.get_logger().info(f"Inizializzato il tello con address: {self.tello.address[0]}")
        self.subscriberC = self.create_subscription(String, "/Command/tello" + i, 10)
        self.subscriberV = self.create_subscription(String, "/viconState/tello" + i, 10) # "String" sbagliata, inserire oggetto restituito dal vicon
        #self.subscriberT = self.create_subscription(String, "telloState/tello", 10)
        #self.publisher_ = self.create_publisher(String, "/telloState/tello" + i, 10)
