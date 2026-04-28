from __future__ import annotations

import os

from robot_interface.backends.ur10 import RobotiqGripperURAdapter, UR10RTDEArmAdapter
from robot_interface.robot import Robot


def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")
    with Robot(
        arm=UR10RTDEArmAdapter(robot_ip=robot_ip),
        gripper=RobotiqGripperURAdapter(host=robot_ip, port=63352),
    ) as robot:
        robot.power_on()

        # Move to block, pick, move to destination, place, then return to a safe pose.
        approach_block = [0.18, -1.05, 1.05, -1.25, -1.30, 0.08]
        pick_block = [0.28, -1.22, 1.18, -1.38, -1.34, 0.11]
        lift_block = [0.14, -0.95, 0.98, -1.15, -1.24, 0.07]
        approach_target = [-0.16, -1.08, 1.08, -1.26, -1.22, -0.02]
        place_block = [-0.26, -1.24, 1.20, -1.40, -1.28, -0.06]
        retreat = [-0.08, -0.92, 0.92, -1.10, -1.16, -0.03]

        robot.open_gripper()
        robot.move_arm_joint(approach_block, speed=0.22, acceleration=0.32)
        robot.move_arm_joint(pick_block, speed=0.18, acceleration=0.28)
        robot.close_gripper()
        robot.move_arm_joint(lift_block, speed=0.24, acceleration=0.34)
        robot.move_arm_joint(approach_target, speed=0.24, acceleration=0.34)
        robot.move_arm_joint(place_block, speed=0.18, acceleration=0.28)
        robot.open_gripper()
        robot.move_arm_joint(retreat, speed=0.24, acceleration=0.34)
        print("Move block around: done")


if __name__ == "__main__":
    main()
