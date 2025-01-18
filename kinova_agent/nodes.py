import cv2
import os
import ollama
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from std_msgs.msg import Float64MultiArray, String
from sensor_msgs.msg import JointState, Image


class AgentPublisher(Node):
    def __init__(self):
        super().__init__("Agent_Publisher")
        self.publisher = self.create_publisher(Float64MultiArray, "published_coordinates", 100)
        self.get_logger().info("Agent Publisher initialised...")
        
    def publish_callback (self, data):
        msg = Float64MultiArray()
        msg.data = data
        self.publisher.publish(msg)
        self.get_logger().info(f"Published coordinates: {msg.data}")


class AgentSubscriber(Node):
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
    

class ImageCapture(Node):
    def __init__(self):
        super().__init__('image_capture_node')
        self.subscription = self.create_subscription(Image, 
                                                     "/camera/color/image_raw", 
                                                     self.image_callback, 
                                                     10)
        self.bridge = CvBridge()
        self.image_path = os.path.join(os.getcwd(), "images")
    
    
    def clear_folder (self):
        """
        Delete all the files if present from the folder
        """
        if os.path.exists(self.image_path): 
            for file_name in os.listdir(self.image_path):
                file_path = os.path.join(self.image_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self.get_logger().info(f"Deleting previous image: {file_path}")
                except Exception as e:
                    self.get_logger().error(f"Failed to delete previously created images: {e}")


    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            
            if not os.path.exists(self.image_path):
                os.makedirs(self.image_path, exist_ok=True)
                
            file_name = os.path.join(self.image_path, "image.png")
            
            self.clear_folder()
            
            # Save the image and check success
            if not cv2.imwrite(filename=file_name, img=cv_image):
                self.get_logger().error(f"Failed to save image to: {file_name}")
            else:
                self.get_logger().info(f"Image successfully saved as: {file_name}")
                self.describe_image()
        except Exception as e:
            self.get_logger().error(f"Failed to save image: {e}")


    def describe_image(self):
        image = os.path.join(self.image_path, "image.png")
        vision_model = "llama3.2-vision"
        try:
            response = ollama.chat(model=vision_model, 
                            messages=
                            [
                                {
                                "role": "user",
                                "content": "Describe what you see in this image",
                                "images": [image]
                                }
                            ],
                            )
            self.get_logger().info(f"\033[1;32m{response['message']['content']}\033[0m")
        except Exception as e:
            self.get_logger().error(f"Error occured while processing image: {e}")
