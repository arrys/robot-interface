from __future__ import annotations

import os
import time

from robot_interface.backends import UR10URScriptArmAdapter
from robot_interface.backends.ur10 import RobotiqGripperURAdapter, UR10RTDEArmAdapter
from robot_interface.interface.arm import CartesianPose, CartesianPosition, Orientation
from robot_interface.robot import Robot


# Table
# y = -550 (left), 550 (right)
# z = 200 (low), 500 (high)
# tool offset is about 200

def main() -> None:
    speed = 0.5
    accel = 0.3
    z_offset = 0
    robot_ip = os.getenv("ROBOT_IP", "192.168.1.200")

    tool_head_down = Orientation(2.27, -2.27, 0.00)
    pos_a = CartesianPose(position=CartesianPosition(900, 0, 500 + z_offset), orientation=tool_head_down)
    pos_b = CartesianPose(CartesianPosition(900, -450, 300 + z_offset), tool_head_down)
    pos_c = CartesianPose(CartesianPosition(900, -450, 250 + z_offset), tool_head_down)
    pos_d = CartesianPose(CartesianPosition(900, 450, 300 + z_offset), tool_head_down)
    pos_e = CartesianPose(CartesianPosition(900, 450, 250 + z_offset), tool_head_down)

    with Robot(
        # arm=UR10RTDEArmAdapter(robot_ip=robot_ip)
        arm=UR10URScriptArmAdapter(robot_ip=robot_ip),
        gripper=RobotiqGripperURAdapter(host=robot_ip, port=63352),
    ) as robot:
        # robot.power_on()
        robot.move_arm_cartesian(pos_a, speed=speed, acceleration=accel)
        robot.open_gripper()
        time.sleep(15)
        while True:
            robot.move_arm_cartesian(pos_b, speed=speed, acceleration=accel)
            time.sleep(5/speed)
            robot.move_arm_cartesian(pos_c, speed=speed, acceleration=accel)
            robot.close_gripper()
            time.sleep(5/speed)
            robot.move_arm_cartesian(pos_b, speed=speed, acceleration=accel)
            time.sleep(5/speed)
            robot.move_arm_cartesian(pos_d, speed=speed, acceleration=accel)
            time.sleep(10/speed)
            robot.move_arm_cartesian(pos_e, speed=speed, acceleration=accel)
            time.sleep(5/speed)
            robot.open_gripper()
            robot.move_arm_cartesian(pos_d, speed=speed, acceleration=accel)
            time.sleep(10/speed)



if __name__ == "__main__":
    main()
