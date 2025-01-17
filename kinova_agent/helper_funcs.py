import re
import rclpy
from .nodes import AgentPublisher, AgentSubscriber, ImageCapture
from sensor_msgs.msg import JointState


def publish_coordinates(coordinates: list) -> None:
    """
    Publishes Coordinates to MoveIt

    Args:
        coordinates (list): command to decide which coordinates to publish
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


def subscribe_to (topic: str, type):
    """
    Subscribe to a topic if available

    Args:
        topic (str): Topic name
    """
    
    try:
        # Initialise the ROS2 Subscriber
        subscriber_node = AgentSubscriber(topic=topic, type=type)
        
        # Spin the Node to keep it publishing
        rclpy.spin_once(subscriber_node, timeout_sec=0.1)
        
        # Return the message
        return subscriber_node.get_message()
    except Exception as e:
        print(f"Error subscribing to Topic: {e}")
    finally:
        subscriber_node.destroy_node()
        
        
def get_direction_coordinates (direction: str):
    """
    Get the coordinates for the direction for

    Args:
        direction (str): The direction the user wants to move the Robot

    Returns:
        Joint States: returns the modified joint states corresponding the direction
    """
    topic_name = "/joint_states" # Topic name to get Joint States
    type_name = JointState  # Type of message to be recieved
    
    joint_states = subscribe_to(topic=topic_name, type=type_name)
    joint_states.insert(0, 0.0) # Add a flag variable for agent_listener.cpp

    # topic_name = "/distance"
    # type_name = String 
    
    distance = 0.5 # default distance we want to move 
    try:
        # distance = subscribe_to(topic=topic_name, type=type_name)
        distance = 0.5 # default distance we want to move 
        if direction == "forward":
            joint_states[2] += distance
            joint_states[4] += (distance * 0.75)
            joint_states[6] -= (distance * 0.3)
        elif direction == "backward":
            joint_states[2] -= distance
            joint_states[4] -= (distance * 0.75)
            joint_states[6] += (distance * 0.3)
        elif direction == "left":
            joint_states[1] -= distance
            joint_states[5] -= (distance * 0.25)
        elif direction == "right":
            joint_states[1] += distance
            joint_states[5] += (distance * 0.25)
        elif direction == "upward":
            joint_states[2] += (distance * 0.5)
            joint_states[4] += distance
            joint_states[6] -= distance * 1.2
        elif direction == "downward":
            joint_states[2] -= (distance * 0.5)
            joint_states[4] -= distance
            joint_states[6] += distance * 1.2
        else:
            print("Direction not found.")
            return
    except Exception as e:
        print(e)
        
    return joint_states


def capture_image():
    # Start the ROS2 Image Subscriber Node
    image_node = ImageCapture()
    
    # Spin the node until an image is processed
    rclpy.spin_once(image_node, timeout_sec=0.1)
    
    # Destroy Node
    image_node.destroy_node()
    
    
    
