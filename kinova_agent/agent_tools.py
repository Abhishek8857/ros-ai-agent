import os
import ollama
from langchain_core.tools import tool, Tool
from .helper_funcs import word_to_num, publish_coordinates, subscribe_to, get_direction_coordinates, capture_image

@tool   
def move_to_home_pose ():
    """
    Moves the Robot arm coordinates for home pose
    """
    # home_pose_coordinates = [1.0, 0.0, 0.5, 0.5, 0.3, -0.5, 0.5, 0.5]
    home_pose_coordinates = [0.0, 0.0, -0.8, -3.15, -2.0, 0.0, -1.2, 1.55]
    publish_coordinates(home_pose_coordinates)
       
       
@tool
def move_to_zero_position ():
    """
    Moves the Robot Arm to Zero Position
    """
    zero_coordinates = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    publish_coordinates(zero_coordinates)
    
     
@tool
def move_forward():
    """
    Moves the Arm forward in the X-direction
    """
    publish_coordinates(get_direction_coordinates("forward"))
    
        
@tool
def move_backward():
    """
    Moves the Arm forward in the X-direction
    """
    publish_coordinates(get_direction_coordinates("backward"))


@tool
def move_left():
    """
    Moves the Arm left in the Y direction
    """
    publish_coordinates(get_direction_coordinates("left"))


@tool
def move_right():
    """
    Moves the Arm right in the Y direction
    """
    publish_coordinates(get_direction_coordinates("right"))


@tool
def move_upwards():
    """
    Moves the Arm upwards in Z direction
    """
    publish_coordinates(get_direction_coordinates("upward"))


@tool
def move_downwards():
    """
    Moves the arm downwards in Z direction
    """
    publish_coordinates(get_direction_coordinates("downward"))


@tool
def open_gripper():
    """
    Opens the Gripper
    """
    open_coordinates = [2.0, -0.0, 0.0]
    publish_coordinates(open_coordinates)


@tool
def close_gripper():
    """
    Closes the Gripper
    """
    close_coordinates = [2.0, 0.8, -0.8]
    publish_coordinates(close_coordinates)


@tool
def describe_what_you_see():
    """
    Describes what the robot sees in the Camera's FOV
    """
    
    # Capture the image
    capture_image()
    
    # Get the image from the saved folder location
    image = os.path.join(os.getcwd(), "images/image.png")
    vision_model = "llama3.2-vision"
    
    # Invoke the VLM Model with the saved image
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
    print(response['message']['content'])


def get_tools () -> list[Tool]:
    return [move_to_home_pose,
            move_to_zero_position,
            move_forward, 
            move_backward,
            move_left,
            move_right,
            move_upwards,
            move_downwards,
            open_gripper, 
            close_gripper,
            describe_what_you_see]
