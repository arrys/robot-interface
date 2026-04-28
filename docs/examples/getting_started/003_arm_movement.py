from __future__ import annotations

import os

from robot_interface.backends.ur10 import UR10RTDEArmAdapter
from robot_interface.interface.arm import CartesianPose, CartesianPosition, Orientation
from robot_interface.robot import Robot

def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")
    with Robot(
        arm=UR10RTDEArmAdapter(robot_ip=robot_ip),
    ) as robot:
        print(f"Before move joints [deg]: {robot.arm_joint_positions_degrees}")
        print(f"Before cartesian pos [mm]: {robot.arm_position_cartesian}")
        joint_target = [0.1, -1.0, 1.1, -1.2, -1.3, 0.1]
        robot.move_arm_joint(joint_target, speed=0.2, acceleration=0.3)
        robot.move_arm_cartesian(
            CartesianPose(
                position=CartesianPosition(-69, -303, 1011),
                orientation=Orientation.from_degrees(-53, -38, -11),
            ),
            speed=0.1,
            acceleration=0.30,
        )
        print(f"After cartesian pos [mm]: {robot.arm_position_cartesian}")


if __name__ == "__main__":
    main()
