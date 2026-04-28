from __future__ import annotations

import os

from robot_interface.backends.ur10 import RobotiqGripperURAdapter, UR10RTDEArmAdapter
from robot_interface.interface.arm import CartesianPose, CartesianPosition, Orientation
from robot_interface.robot import Robot


def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")
    with Robot(
        arm=UR10RTDEArmAdapter(robot_ip=robot_ip),
        gripper=RobotiqGripperURAdapter(host=robot_ip, port=63352),
    ) as robot:
        robot.power_on()

        orientation = Orientation.from_degrees(-53, -38, -11)
        approach_block = CartesianPose(CartesianPosition(-120, -310, 1020), orientation)
        pick_block = CartesianPose(CartesianPosition(-120, -310, 990), orientation)
        lift_block = CartesianPose(CartesianPosition(-120, -310, 1040), orientation)
        approach_target = CartesianPose(CartesianPosition(130, -300, 1020), orientation)
        place_block = CartesianPose(CartesianPosition(130, -300, 990), orientation)
        retreat = CartesianPose(CartesianPosition(80, -260, 1060), orientation)

        robot.open_gripper()
        robot.move_arm_cartesian(approach_block, speed=0.10, acceleration=0.30)
        robot.move_arm_cartesian(pick_block, speed=0.08, acceleration=0.25)
        robot.close_gripper()
        robot.move_arm_cartesian(lift_block, speed=0.10, acceleration=0.30)
        robot.move_arm_cartesian(approach_target, speed=0.10, acceleration=0.30)
        robot.move_arm_cartesian(place_block, speed=0.08, acceleration=0.25)
        robot.open_gripper()
        robot.move_arm_cartesian(retreat, speed=0.10, acceleration=0.30)
        print("Move block around (cartesian): done")


if __name__ == "__main__":
    main()
