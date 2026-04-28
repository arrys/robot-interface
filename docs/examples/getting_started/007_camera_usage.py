from __future__ import annotations

import os

from robot_interface.backends.mock import MockCameraAdapter
from robot_interface.backends.ur10 import RobotiqGripperURAdapter, UR10RTDEArmAdapter
from robot_interface.robot import Robot

def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")
    with Robot(
        arm=UR10RTDEArmAdapter(robot_ip=robot_ip),
        gripper=RobotiqGripperURAdapter(host=robot_ip, port=63352),
    ) as robot:
        robot.power_on()
        robot.move_arm_joint(
            [0.10, -0.90, 0.95, -1.15, -1.20, 0.05],
            speed=0.20,
            acceleration=0.30,
        )
        _, width, height = robot.capture_frame()
        print(f"Camera: size={width}x{height}")


if __name__ == "__main__":
    main()
