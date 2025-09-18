import rclpy
from .nodes import AgentPublisher, AgentSubscriber, ImageCapture
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray, Bool


def publish_to(type_name, topic_name: str, coordinates: list = None, msg: bool = None) -> None:
    """
    Publishes Coordinates to MoveIt

    Args:
        coordinates (list) = None :  Desired coordinates to publish
        msg (bool) = None : Desired Bool Message to publish
    """
    try:
        # Initialise the ROS2 Node to publish the coordinates
        publisher_node = AgentPublisher(type=type_name, topic=topic_name)
        if type_name == Float64MultiArray:
            publisher_node.publish_callback(coordinates)
        elif type_name == Bool:
            publisher_node.publish_callback(msg)
        
        # Spin the Node to keep it publishing
        rclpy.spin_once(publisher_node, timeout_sec=0.1)

        # Destroy Node
        publisher_node.destroy_node()
    except Exception as e:
        print(f"Error Publishing Coordinates to Robot: {e}")
        return
    finally:
        publisher_node.destroy_node()
    

def subscribe_to (topic_name: str, type_name):
    """
    Subscribe to a topic if available

    Args:
        topic (str): Topic name
        type_name : Type of the message to be recieved
    """
    
    try:
        # Initialise the ROS2 Subscriber
        subscriber_node = AgentSubscriber(type=type_name, topic=topic_name)
        
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
    
    joint_states = subscribe_to(topic_name=topic_name, type_name=type_name)
    joint_states.insert(0, 0.0) # Add a flag variable for agent_listener.cpp
    
    distance = 0.5 # default distance we want to move 
    try:
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
        elif direction == "right":
            joint_states[1] += distance
        elif direction == "upward":
            joint_states[2] += (distance * 0.2)
            joint_states[4] += distance * 1.2
            joint_states[6] -= distance
        elif direction == "downward":
            joint_states[2] += (distance * 0.2)
            joint_states[4] -= distance
            joint_states[6] += distance * 1.2
        elif direction == "clockwise":
            joint_states[7] -= distance * 3.25
        elif direction == "anticlockwise":
            joint_states[7] += distance * 3.25
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
    
    
    
