from ..shared.models.robot import Robot
from dotenv import load_dotenv
import os, atexit, re

load_dotenv()

if __name__ == "__main__" :
    robot = Robot("192.168.1.2")
    robot.pick_and_place_vials([("P24", "C3"), ("A1", "C4")])
    
    atexit.register(robot.disconnection)
