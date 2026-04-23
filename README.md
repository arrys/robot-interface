# Universal Robot Interface

Python package for robot, gripper, and camera integration adapter.

Two available examples include the mock adapter and the ur10 adapter.

## Examples
- [000 Connect RTDE Arm](docs/examples/getting_started/000_connect_rtde_arm.py)
- [001 Connect URScript Arm](docs/examples/getting_started/001_connect_urscript_arm.py)
- [002 Connect UR Gripper](docs/examples/getting_started/002_connect_ur_gripper.py)
- [003 Move](docs/examples/getting_started/003_move.py)
- [004 Pick and place](docs/examples/getting_started/004_pick_and_place.py)
- [005 Camera usage](docs/examples/getting_started/005_camera_usage.py)
- [006 Gripper socket](docs/examples/getting_started/006_gripper_socket.py)

UR10 joint order for all `move_arm_joint([...])` vectors:
`[Base, Shoulder, Elbow, Wrist1, Wrist2, Wrist3]`

## Configuration
Set robot connection with environment variables first:

```bash
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/003_move.py
```

Examples read `ROBOT_IP` from environment and default to `127.0.0.1`.

## Running Getting Started
Run any getting-started example with:

```bash
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/000_connect_rtde_arm.py
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/001_connect_urscript_arm.py
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/002_connect_ur_gripper.py
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/003_move.py
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/004_pick_and_place.py
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/005_camera_usage.py
ROBOT_IP=127.0.0.1 uv run python docs/examples/getting_started/006_gripper_socket.py
```

These scripts are no-flag examples wired directly for `ur10` and use `ROBOT_IP` with default `127.0.0.1`.

## Documentation
- [Installation](docs/installation.md)
- [Getting Started Examples](docs/examples/getting_started/)