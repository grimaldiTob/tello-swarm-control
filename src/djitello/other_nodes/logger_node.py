import rclpy
from rclpy.node import Node
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from custom_msgs.msg import TelloStatus

class Logger_Node(Node):

    def __init__(self):
        super().__init__("Logger_Node")

        self.init_subscription()

        self.pose_data = []
        self.error_data = []
        self.get_logger().info('Logger Node avviato e in ascolto')


    def init_subscription(self):
        self.pose_sub = self.create_subscription(TelloStatus, "/Tello/pose", self.pose_callback, 10)
        self.error_sub = self.create_subscription(TelloStatus, "/Tello/error", self.error_callback, 10)


    def pose_callback(self, msg:TelloStatus):
        timestamp = self.get_clock().now().nanoseconds * 1e-9
        self.pose_data.append({
            'timestamp': timestamp,
            'id': msg.id,
            'x': msg.x,
            'y': msg.y,
            'z': msg.z
        })
    
    def error_callback(self, msg:TelloStatus):
        timestamp = self.get_clock().now().nanoseconds * 1e-9
        self.error_data.append({
            'timestamp': timestamp,
            'id':msg.id,
            'x': msg.x,
            'y': msg.y,
            'z': msg.z
        })

    def destroy_node(self):
        self.plot_pose()


        # Chiamo lo shutdown del nodo
        super().destroy_node()

    def plot_pose(self):
        df = pd.DataFrame(self.pose_data)
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_name = f'drones_log_{timestamp_str}.csv'
        df.to_csv(csv_name, index=False)
        self.get_logger().info(f'Dati salvati in {csv_name}')

        plt.figure()
        for drone_id in df['id'].unique():
            plt.plot(df[df['id'] == drone_id]['x'], df[df['id'] == drone_id]['y'], label="Tello " + str(drone_id))

        plt.xlabel('X [m]')
        plt.ylabel('Y [m]')
        plt.title('Traiettoria dei droni')
        plt.grid(True)
        plt.axis('equal')
        plt.legend()
        png_name = f'drones_plot_{timestamp_str}.png'
        plt.savefig(png_name)
        self.get_logger().info(f'Grafico salvato in {png_name}')
        plt.close()

    def plot_error(self):
        df = pd.DataFrame(self.error_data)
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_name = f'error_log_{timestamp_str}.csv'
        df.to_csv(csv_name, index=False)
        self.get_logger().info(f'Dati salvati in {csv_name}')

        for drone_id in df['id'].unique():
            for l in ['x', 'y', 'z']:
                plt.plot(df[df['id'] == drone_id]['timestamp'], df[df['id'] == drone_id][l], label="Error_" + l)
            plt.xlabel('Time[s]')
            plt.ylabel('Error[m]')
            plt.title('Errori per il tello ' + str(drone_id))
            plt.grid(True)
            plt.legend()
            png_name = f'error_t1_plot_{timestamp_str}.png'
            plt.savefig(png_name)
            self.get_logger().info(f'Grafico salvato in {png_name}')
            plt.close()

def main():
    rclpy.init(args=None)
    node = Logger_Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

