import rclpy
from langchain_core.tools import tool, Tool
import rclpy.executors
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String
from .helper_funcs import word_to_num


class AgentPublisher (Node):
    def __init__(self):
        super().__init__("Agent_Publisher")
        self.publisher = self.create_publisher(Float64MultiArray, "published_coordinates", 100)
        self.get_logger().info("Agent Publisher initialised and ready to publish")
        
    def publish_coordinates (self, data):
        msg = Float64MultiArray()
        msg.data = data
        self.publisher.publish(msg)
        self.get_logger().info(f"Published coordinates: {msg.data}")


class AgentSubscriber (Node):
    def __init__(self):
        super().__init__("Agent_Subscriber")
        self.subscriber = self.create_subscription(String, "transcription_text", self.subscriber_callback, 100)
        self.distance = None
        self.recieved = False
        self.subscriber
        
    def subscriber_callback(self, msg):
        """
        Callback function to process the recieved message
        """
        try:
            self.distance = word_to_num(msg.data)
            self.recieved = True
            self.get_logger().info(f"Recieved Message: {msg.data}")
            self.get_logger().info(f"Moving by {self.distance} units.")
        except Exception as error:
            self.get_logger().error(f"Error processing message: {error}")
            
        
@tool   
def move_to_home_pose ():
    """
    Sends Robot arm coordinates for home pose
    """
    # home_pose_coordinates = [1.0, 0.0, 0.5, 0.5, 0.3, -0.5, 0.5, 0.5]
    home_pose_coordinates = [0.0, 0.0, -0.8, -3.15, -2.0, 0.0, -1.2, 1.55]
    
    # Initialise the ROS2 Node to publish the coordinates
    agent_publisher_node = AgentPublisher()
    agent_publisher_node.publish_coordinates(home_pose_coordinates)
    
    # Spin the Node to keep it publishing
    rclpy.spin_once(agent_publisher_node, timeout_sec=2)

    # Destroy Node
    agent_publisher_node.destroy_node()


@tool
def move_forward():
    """
    Moves the Arm forward in the X-direction
    """
    agent_subscriber_node = AgentSubscriber()
    agent_subscriber_node.get_logger().info("By how much?")
    
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(agent_subscriber_node)
    
    # Wait until the subscriber recieves a valid input
    while not agent_subscriber_node.recieved:
        executor.spin_once(timeout_sec=0.1)
    
    # Retrieve the distance
    distance = agent_subscriber_node.distance
    agent_subscriber_node.get_logger().info(f"Recieved Distance {distance}")

    # Clean up the subscriber Node
    agent_subscriber_node.destroy_node()

    # Define new pose Coordinates based on recieved distance
    coordinates = [1.0, 0.0, -0.1, 0.5, 0.5, -0.5, 0.5, 0.5]
    # coordinates = [0.0, 0.0, 0.0 + distance, -3.15, -2.0 + distance, 0.005, -1.2, 1.55]
    
    # Initialise the ROS2 Node to publish the coordinates
    agent_publisher_node = AgentPublisher()
    agent_publisher_node.publish_coordinates(coordinates)
    executor.add_node(agent_publisher_node)
    
    # Spin the Node to keep it publishing
    rclpy.spin_once(agent_publisher_node, timeout_sec=1.0)
    
    # Destroy the created Nodes
    agent_publisher_node.destroy_node()


@tool
def move_backward():
    """
    Moves the Arm forward in the X-direction
    """
    pass


@tool
def move_left():
    """
    Moves the Arm left in the Y direction
    """
    pass


@tool
def move_right():
    """
    Moves the Arm right in the Y direction
    """
    pass


@tool
def move_upwards() -> None:
    """
    Moves the Arm upwards in Z direction
    """
    pass


@tool
def move_downwards() -> None:
    """
    Moves the arm downwards in Z direction
    """
    pass


@tool
def open_gripper():
    """
    Opens the Gripper
    """
    coordinates = [2.0, 0.0, 0.0]

    # Initialise the ROS2 Node to publish the coordinates
    agent_publisher_node = AgentPublisher()
    agent_publisher_node.publish_coordinates(coordinates)
    
    # Spin the Node to keep it publishing
    rclpy.spin_once(agent_publisher_node, timeout_sec=2)

    # Destroy Node
    agent_publisher_node.destroy_node()


@tool
def close_gripper():
    """
    Closes the Gripper
    """
    coordinates = [2.0, 0.8, -0.8]
    
    # Initialise the ROS2 Node to publish the coordinates
    agent_publisher_node = AgentPublisher()
    agent_publisher_node.publish_coordinates(coordinates)
    
    # Spin the Node to keep it publishing
    rclpy.spin_once(agent_publisher_node, timeout_sec=2)

    # Destroy Node
    agent_publisher_node.destroy_node()



def get_tools () -> list[Tool]:
    return [move_to_home_pose, 
            move_forward, 
            move_backward, 
            open_gripper, 
            close_gripper]
