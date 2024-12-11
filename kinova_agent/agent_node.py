import rclpy
import time 

from rclpy.node import Node
from std_msgs.msg import String
from .llm import get_llm
from .agent_tools import get_tools
from .agent import KinovaAgent

class Agent(Node):
    def __init__(self):
        super().__init__("Kinova_Agent")
        self.publisher = self.create_publisher(String, "agent_response", 100)
        self.subscription = self.create_subscription(String, "transcription_text", self.agent_callback , 10)
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
        # Extract and log only the response message content
        # self.get_logger().info(f"Agent response: {response.content}")
        
        # Wait for a few seconds
        time.sleep(2.0)
        
        # Create and Publish the agent response
        # publish_msg = String()
        # publish_msg.data = response.content
        # self.publisher.publish(publish_msg)
        # self.get_logger().info(f"Publishing agent response: {response.content}")

        # Wait for the next message
        self.get_logger().info(f"Waiting for the next message ...\n")

    
    
    
def main ():
    rclpy.init()
    node = Agent()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt received, shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
