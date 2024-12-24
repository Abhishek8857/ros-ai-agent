from langchain_core.tools import tool, Tool
from .helper_funcs import word_to_num, publish_coordinates, subscribe_to

@tool   
def move_to_home_pose (query):
    """
    Sends Robot arm coordinates for home pose
    """
    # home_pose_coordinates = [1.0, 0.0, 0.5, 0.5, 0.3, -0.5, 0.5, 0.5]
    home_pose_coordinates = [0.0, 0.0, -0.8, -3.15, -2.0, 0.0, -1.2, 1.55]
    publish_coordinates(home_pose_coordinates)
    

@tool
def move_forward():
    """
    Moves the Arm forward in the X-direction
    """
    # # Create a subscriber instance  
    # agent_subscriber_node = AgentSubscriber()
    # recieved_message = None
    # agent_subscriber_node.get_logger().info("By how much?")
    # rclpy.spin_once(agent_subscriber_node, timeout_sec=2)
    # # rclpy.spin(agent_subscriber_node)

    
    # # Get the distance to be moved 
    # recieved_message = agent_subscriber_node.get_message()
    
    # Get distance from the message
    # distance = word_to_num(recieved_message)
    distance = 1
    fwd_coordinates = [0.0, 0.0, round(-0.8 + distance, ndigits=2), -3.15, round(-2.0 + distance, ndigits=2), 0.005, -1.2, 1.55]
    publish_coordinates(fwd_coordinates)

        
@tool
def move_backward():
    """
    Moves the Arm forward in the X-direction
    """
    distance = 1
    fwd_coordinates = [0.0, 0.0, round(-0.8 - distance, ndigits=2), -3.15, round(-2.0 - distance, ndigits=2), 0.005, -1.2, 1.55]
    publish_coordinates(fwd_coordinates)


@tool
def move_left():
    """
    Moves the Arm left in the Y direction
    """
    distance = 1
    fwd_coordinates = [0.0, 0.0, round(-0.8 - distance, ndigits=2), -3.15, round(-2.0 - distance, ndigits=2), 0.005, -1.2, 1.55]
    publish_coordinates(fwd_coordinates)


@tool
def move_right():
    """
    Moves the Arm right in the Y direction
    """
    distance = 1
    fwd_coordinates = [0.0, 0.0, round(-0.8 - distance, ndigits=2), -3.15, round(-2.0 - distance, ndigits=2), 0.005, -1.2, 1.55]
    publish_coordinates(fwd_coordinates)


@tool
def move_upwards():
    """
    Moves the Arm upwards in Z direction
    """
    distance = 1
    fwd_coordinates = [0.0, 0.0, round(-0.8 - distance, ndigits=2), -3.15, round(-2.0 - distance, ndigits=2), 0.005, -1.2, 1.55]
    publish_coordinates(fwd_coordinates)


@tool
def move_downwards():
    """
    Moves the arm downwards in Z direction
    """
    distance = 1
    fwd_coordinates = [0.0, 0.0, round(-0.8 - distance, ndigits=2), -3.15, round(-2.0 - distance, ndigits=2), 0.005, -1.2, 1.55]
    publish_coordinates(fwd_coordinates)


@tool
def open_gripper():
    """
    Opens the Gripper
    """
    open_coordinates = [2.0, 0.0, 0.0]
    publish_coordinates(open_coordinates)


@tool
def close_gripper():
    """
    Closes the Gripper
    """
    close_coordinates = [2.0, 0.8, -0.8]
    publish_coordinates(close_coordinates)


def get_tools () -> list[Tool]:
    return [move_to_home_pose, 
            move_forward, 
            move_backward,
            open_gripper, 
            close_gripper]
