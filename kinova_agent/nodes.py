from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from std_msgs.msg import Float64MultiArray, String
from sensor_msgs.msg import JointState


class AgentPublisher (Node):
    def __init__(self):
        super().__init__("Agent_Publisher")
        self.publisher = self.create_publisher(Float64MultiArray, "published_coordinates", 100)
        self.get_logger().info("Agent Publisher initialised...")
        
    def publish_callback (self, data):
        msg = Float64MultiArray()
        msg.data = data
        self.publisher.publish(msg)
        self.get_logger().info(f"Published coordinates: {msg.data}")


class AgentSubscriber (Node):
    def __init__(self, topic: str, type):
        super().__init__("Agent_Subscriber")
        qos_profile = QoSProfile(depth=1, durability=QoSDurabilityPolicy.VOLATILE)
        self.topic = topic
        self.type = type
        
        self.subscriber = self.create_subscription(self.type, self.topic, self.subscriber_callback, qos_profile=qos_profile)
        self.get_logger().info("Agent Subscriber Initialised...")
        self.recieved_message = None
        self.subscriber
        
    def subscriber_callback(self, msg):
        """
        Callback function to return the recieved message
        """
        self.get_logger().info("Waiting for tool query to be published")
        if self.type == String or self.type == Float64MultiArray:
            self.recieved_message = msg.data
        elif self.type == JointState:
            self.recieved_message = {
            "name": msg.name,
            "position": list(msg.position),
            "velocity": list(msg.velocity),
            "effort": list(msg.effort)
            }
        
        self.get_logger().info(f"Recieved Joint states: {self.recieved_message}")

        
            
    def get_message(self):
        """
        Getter function to return the recieved message
        """
        if self.recieved_message is None:
            raise ValueError("No message received. Please check the publisher.")
        msg = self.recieved_message
        
        if self.type == JointState:
            coordinates = []
            for i in range(1, 8):
                if f"joint_{i}" in msg["name"]:
                    joint_index = msg["name"].index(f"joint_{i}")
                    coordinates.append(msg["position"][joint_index])

            return coordinates
        
        self.recieved_message = None
        return msg
    