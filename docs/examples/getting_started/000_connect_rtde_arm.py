from __future__ import annotations

import os

from robot_interface.backends.ur10 import UR10RTDEArmAdapter
from robot_interface.robot import Robot


def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")

    try:
        with Robot(arm=UR10RTDEArmAdapter(robot_ip=robot_ip)) as robot:
            print("RTDE arm: connected")
            print(robot.arm_joint_positions_degrees)
            print(robot.arm_joint_positions_radians)
            print(robot.arm_position_cartesian)
            print(robot.arm_orientation)
    except Exception as exc:
        print(f"RTDE arm: connection failed ({exc})")


if __name__ == "__main__":
    main()
