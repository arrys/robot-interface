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

        # Joint order: [Base, Shoulder, Elbow, Wrist1, Wrist2, Wrist3]
        approach_joints = [0.20, -1.10, 1.10, -1.30, -1.40, 0.10]
        grasp_joints = [0.35, -1.35, 1.30, -1.50, -1.45, 0.15]
        lift_joints = [0.15, -1.00, 1.00, -1.20, -1.35, 0.10]
        place_joints = [-0.20, -1.20, 1.15, -1.40, -1.30, -0.05]
        retreat_joints = [-0.10, -1.00, 0.95, -1.10, -1.20, -0.05]

        robot.move_arm_joint(approach_joints, speed=0.25, acceleration=0.35)
        robot.move_arm_joint(grasp_joints, speed=0.20, acceleration=0.30)
        robot.close_gripper()
        robot.move_arm_joint(lift_joints, speed=0.25, acceleration=0.35)
        input("Press any key to continue...")
        robot.move_arm_joint(place_joints, speed=0.25, acceleration=0.35)
        robot.open_gripper()
        robot.move_arm_joint(retreat_joints, speed=0.25, acceleration=0.35)
        print("Pick and place: done")


if __name__ == "__main__":
    main()
