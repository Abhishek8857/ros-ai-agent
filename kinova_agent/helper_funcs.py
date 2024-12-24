import re
import rclpy
from .nodes import AgentPublisher, AgentSubscriber


WORD_TO_NUMBER = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


def word_to_num (query):
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


def publish_coordinates(coordinates: list) -> None:
    """
    Publishes Coordinates to MoveIt

    Args:
        coodirnates (list): command to decide which coordinates to publish
    """
    try:
        # Initialise the ROS2 Node to publish the coordinates
        publisher_node = AgentPublisher()
        publisher_node.publish_callback(coordinates)
        
        # Spin the Node to keep it publishing
        rclpy.spin_once(publisher_node, timeout_sec=0.1)

        # Destroy Node
        publisher_node.destroy_node()
    except Exception as e:
        print(f"Error Publishing Coordinates to Robot: {e}")
        return
    finally:
        publisher_node.destroy_node()

def subscribe_to (topic: str):
    """
    Subscribe to a topic if available

    Args:
        topic (str): Topic name
    """
    
    try:
        # Initialise the ROS2 Subscriber
        subscriber_node = AgentSubscriber(topic)
        
        # Spin the Node to keep it publishing
        rclpy.spin_once(subscriber_node, timeout_sec=0.1)
        
        # Return the message
        return subscriber_node.get_message()
    except Exception as e:
        print(f"Error subscribing to Topic: {e}")
    finally:
        subscriber_node.destroy_node()
        
        