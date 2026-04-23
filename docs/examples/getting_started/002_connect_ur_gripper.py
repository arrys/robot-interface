from __future__ import annotations

import os

from robot_interface.backends.ur10 import RobotiqGripperURAdapter
from robot_interface.robot import Robot


def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")
    try:
        with Robot(
            gripper=RobotiqGripperURAdapter(host=robot_ip, port=63352),
        ) as robot:
            before = robot.gripper_position
            robot.set_gripper(before)
            after = robot.gripper_position
            print(f"UR gripper: connected, position={after:.2f}%")
    except Exception as exc:
        print(f"UR gripper: read failed ({exc})")


if __name__ == "__main__":
    main()
