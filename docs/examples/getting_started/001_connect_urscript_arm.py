from __future__ import annotations

import os

from robot_interface.backends.ur10 import UR10URScriptArmAdapter
from robot_interface.robot import Robot


def main() -> None:
    robot_ip = os.getenv("ROBOT_IP", "127.0.0.1")
    try:
        with Robot(arm=UR10URScriptArmAdapter(robot_ip=robot_ip)) as robot:
            robot.power_on()
            robot.brake_release()
            print("URScript arm: connected")
    except Exception as exc:
        print(f"URScript arm: connection failed ({exc})")


if __name__ == "__main__":
    main()
