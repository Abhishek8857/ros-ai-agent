import rclpy
from langchain_core.tools import tool, Tool
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class PublishMessage (Node):
    def __init__(self):
        super().__init__("Agent_Publisher")
        self.publisher = self.create_publisher(Float64MultiArray, "cartesian_coordinates", 100)
        self.get_logger().info("Agent Publisher initialised and ready to publish")
        
    def publish_coordinates (self, data):
        msg = Float64MultiArray()
        msg.data = data
        self.publisher.publish(msg)
        self.get_logger().info(f"Published coordinates: {msg.data}")


@tool
def move_to_home_pose () -> None:
    """
    Sends Robot arm coordinates for home pose

    Returns:
        list: list with Cartesian Coordinates
    """
    home_pose_coordinates = [0.0, -0.94, -3.15, -2.13, 0.05, -1.2, 1.5]
    
    # Initialise the ROS2 Node to publish the coordinates
    agent_node = PublishMessage()
    agent_node.publish_coordinates(home_pose_coordinates)
    
    # Spin the Node to keep it publishing
    rclpy.spin_once(agent_node, timeout_sec=2)
    
    
def get_tools () -> list[Tool]:
    return [move_to_home_pose]
