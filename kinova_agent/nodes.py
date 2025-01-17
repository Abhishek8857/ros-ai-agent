import cv2
import os
import ollama
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from std_msgs.msg import Float64MultiArray, String
from sensor_msgs.msg import JointState, Image
from PIL import Image


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
        super().__init__('camera_node')
        self.subscription = self.create_subscription(Image, 
                                                     "/camera/color/image_raw", 
                                                     self.image_callback, 
                                                     10)
        self.bridge = CvBridge()
        self.image_path = os.path.join(os.getcwd(), "image")
    
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
    
    def describe_image(self):
        image = cv2.imread(os.path.join(self.image_path, "image.png"))
        vision_model = "llama3.2-vision"

        processed_image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
        processed_image = cv2.convertScaleAbs(processed_image, alpha=1.2, beta=30)
        processed_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
        
        response = ollama.chat(model=vision_model, 
                        messages=
                        [
                            {
                            "role": "user",
                            "content": "Describe all objects in brief with distinguishing characteristics, no matter how small.",
                            "images": [processed_image]
                            }
                        ],
                        )
        self.get_logger().info(f"\033[1;32m{response['message']['content']}\033[0m")

        
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
                self.get_logger().info("Processing image ...")
                self.describe_image()
        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")


class WordToNum(Node):
    def __init__(self):
        super().__init__("word_to_num")
        
        qos_profile = QoSProfile(depth=1, durability=QoSDurabilityPolicy.VOLATILE)
        self.subscribe = self.create_subscription(String, "transcription_text", self.word_to_num_callback,qos_profile=qos_profile)
        self.publish = self.create_publisher(String, "distance", qos_profile=qos_profile)
        self.get_logger().info("Word to num Node initialised....")
        self.subscribe

    def word_to_num_callback(self, msg):
        try:
            # Convert the recieved message to a number
            converted_number = self.word_to_num(msg.data)
            self.get_logger().info("Converted message data into distance")

            # Publish the converted number
            number_msg = String()
            number_msg.data = str(converted_number)
        
        except ValueError as e:
            if "Invalid query" in str(e):
                self.get_logger().info("No Number in this query. Skipping query")
          