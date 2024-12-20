import rclpy
import rclpy.executors
from rclpy.time import Time
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from std_msgs.msg import String
from .llm import get_llm
from .agent import KinovaAgent



class Agent(Node):
    def __init__(self):
        super().__init__("Kinova_Agent")
        qos_profile = QoSProfile(depth=10, durability=QoSDurabilityPolicy.VOLATILE)
        self.publisher = self.create_publisher(String, "agent_response", 100)
        self.subscription = self.create_subscription(String, "transcription_text", self.agent_callback , qos_profile=qos_profile)
        self.subscription
        
        self.get_logger().info("Kinova Agent initialised and waiting for messages ...")
        self.message_recieved = False

        
    def agent_callback (self, msg):
        """Callback function to process recieved transcription text"""
        
        self.get_logger().info("Waiting for message to be published ...")
        
        if not self.message_recieved:
            self.message_recieved = True
        
        
        self.get_logger().info(f"Recieved message: {msg.data}")
        self.get_logger().info(f"Invoking Agent with the query [{msg.data}]")

        agent = KinovaAgent(llm=get_llm())
                
        response = agent.invoke([msg.data])
        self.get_logger().info(response)

        # Wait for the next message
        self.message_recieved = False
        self.get_logger().info(f"Waiting for the next message ...\n")


def main ():
    rclpy.init()
    kinova_node = Agent()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(kinova_node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        kinova_node.get_logger().info("Keyboard interrupt received, shutting down...")
    finally:
        executor.remove_node(kinova_node)
        kinova_node.destroy_node()
        rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
