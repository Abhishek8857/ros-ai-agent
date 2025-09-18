import rclpy
import re
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, QoSDurabilityPolicy


WORD_TO_NUMBER = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


class WordToNum(Node):
    def __init__(self):
        super().__init__("word_to_num")
        
        qos_profile = QoSProfile(depth=1, durability=QoSDurabilityPolicy.VOLATILE)
        self.subscriber = self.create_subscription(String, "transcription_text", self.word_to_num_callback, qos_profile=qos_profile)
        self.publisher = self.create_publisher(String, "distance", qos_profile=qos_profile)
        self.get_logger().info("Word to num Node initialised....")
        self.subscriber
        
    def word_to_num(self, query):
        """
        Converts words representing numbers to their numerical equivalent.
        Supports small numbers and phrases like "By 2 Units"
        """

        words = query.lower().strip()
    
        # Check if the input contains numerical digits
        match = re.search(r'\b\d+\b', words)
        if match:
            number = int(match.group())
            if 1 <= number <= 10:
                return number
            else:
                raise ValueError("Number out of range. Only numbers from 1 to 10 are allowed.")
        
        # Check for word representation of numbers
        for word in words.split():
            if word in WORD_TO_NUMBER:
                return WORD_TO_NUMBER[word]
        
        raise ValueError("Invalid query. Please provide a number between 1 and 10")


    def word_to_num_callback(self, msg):
        try:
            # Convert the recieved message to a number
            converted_number = self.word_to_num(msg.data)
            self.get_logger().info("Converted message data into distance")

            # Publish the converted number
            number_msg = String()
            number_msg.data = str(converted_number)
            self.publisher.publish(number_msg)
            
        except ValueError as e:
            if "Invalid query" in str(e):
                self.get_logger().info("No Number in this query. Skipping query")
                
            
        
def main ():
    rclpy.init()
    word_to_num_node = WordToNum()
    try:
        rclpy.spin(word_to_num_node)
    except KeyboardInterrupt:
        word_to_num_node.get_logger().info("Keyboard interrupt received, shutting down...")
    finally:
        word_to_num_node.destroy_node()
        rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
