from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from robot_interface.backends.mock import MockArmAdapter, MockCameraAdapter, MockGripperAdapter
from robot_interface.interface.arm import CartesianPose, CartesianPosition, Orientation
from robot_interface.robot import Robot


def test_core_commands_cover_basic_motion_and_gripper() -> None:
    robot = Robot(arm=MockArmAdapter(), gripper=MockGripperAdapter(), camera=MockCameraAdapter())

    robot.move_arm_cartesian(
        CartesianPose(position=CartesianPosition(0.4, -0.2, 0.3), orientation=Orientation(0.0, 3.14, 0.0))
    )
    pose = robot.arm_position_cartesian
    assert pose.x == 0.4

    robot.set_gripper(35)
    percent = robot.gripper_position
    assert 0.0 <= percent <= 100.0


def test_additional_debug_commands_return_typed_data() -> None:
    robot = Robot(arm=MockArmAdapter(), gripper=MockGripperAdapter(), camera=MockCameraAdapter())

    gripper_debug = robot.debug_gripper()
    camera_debug = robot.debug_camera()

    assert gripper_debug.backend == "mock_gripper"
    assert camera_debug.backend == "mock_camera"


def _save_xy_plot(
    points: list[CartesianPose],
    out_path: Path,
    title: str,
    control_poses: list[CartesianPose] | None = None,
) -> None:
    xs = [p.position.x for p in points]
    ys = [p.position.y for p in points]
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(xs, ys, "-", linewidth=1.8)
    ax.scatter(xs, ys, s=22, label="interpolated points")
    if control_poses:
        cxs = [p.position.x for p in control_poses]
        cys = [p.position.y for p in control_poses]
        ax.scatter(cxs, cys, s=54, marker="x", label="input poses")
    ax.scatter([xs[0], xs[-1]], [ys[0], ys[-1]], s=44, label="start/end")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def test_interpolate_cartesian_path_with_2_or_3_control_points(tmp_path: Path) -> None:
    arm = MockArmAdapter()
    segments = 24
    orientation = Orientation(0.0, 0.2, -0.1)

    for control_points in (2, 3):
        path: list[CartesianPose] = []
        for i in range(control_points):
            t = i / (control_points - 1)
            x = 100.0 * t
            y = 30.0 * math.sin(t * math.pi)
            z = 5.0 + 10.0 * t
            path.append(CartesianPose(CartesianPosition(x, y, z), orientation))

        interpolated = arm.interpolate_cartesian_path(path, segments=segments)
        assert len(interpolated) == segments + 1
        assert interpolated[0].position.x == pytest.approx(path[0].position.x)
        assert interpolated[0].position.y == pytest.approx(path[0].position.y)
        assert interpolated[0].position.z == pytest.approx(path[0].position.z)
        assert interpolated[-1].position.x == pytest.approx(path[-1].position.x)
        assert interpolated[-1].position.y == pytest.approx(path[-1].position.y)
        assert interpolated[-1].position.z == pytest.approx(path[-1].position.z)
        assert interpolated[0].orientation == path[0].orientation
        assert interpolated[-1].orientation == path[-1].orientation

        if control_points == 2:
            mid = interpolated[len(interpolated) // 2]
            assert mid.position.x == pytest.approx(50.0)
            assert mid.position.y == pytest.approx(0.0)
            assert mid.position.z == pytest.approx(10.0)

        if control_points == 3:
            mid = interpolated[len(interpolated) // 2]
            assert mid.position.x == pytest.approx(path[1].position.x)
            assert mid.position.y == pytest.approx(path[1].position.y)
            assert mid.position.z == pytest.approx(path[1].position.z)
            y_values = [p.position.y for p in interpolated[1:-1]]
            assert max(abs(y) for y in y_values) > 1e-6

        plot_path = tmp_path / f"interpolation_{control_points}_points.png"
        _save_xy_plot(interpolated, plot_path, f"Interpolated path with {control_points} control points", path)
        assert plot_path.exists()


def test_interpolate_cartesian_path_rejects_more_than_3_points() -> None:
    arm = MockArmAdapter()
    orientation = Orientation(0.0, 0.0, 0.0)
    path = [
        CartesianPose(CartesianPosition(0.0, 0.0, 0.0), orientation),
        CartesianPose(CartesianPosition(10.0, 10.0, 0.0), orientation),
        CartesianPose(CartesianPosition(20.0, -10.0, 0.0), orientation),
        CartesianPose(CartesianPosition(30.0, 0.0, 0.0), orientation),
    ]
    with pytest.raises(ValueError, match="exactly 2 poses \\(line\\) or 3 poses \\(curve through all points\\)"):
        arm.interpolate_cartesian_path(path, segments=8)


def test_interpolate_cartesian_path_three_poses_seven_segments(tmp_path: Path) -> None:
    arm = MockArmAdapter()
    orientation = Orientation(0.0, 0.1, -0.2)
    path = [
        CartesianPose(CartesianPosition(0.0, 0.0, 5.0), orientation),
        CartesianPose(CartesianPosition(50.0, 30.0, 10.0), orientation),
        CartesianPose(CartesianPosition(100.0, 0.0, 15.0), orientation),
    ]
    segments = 7
    interpolated = arm.interpolate_cartesian_path(path, segments=segments)

    assert len(interpolated) == 8
    assert interpolated[0].position.x == pytest.approx(path[0].position.x)
    assert interpolated[-1].position.x == pytest.approx(path[-1].position.x)

    mid = interpolated[len(interpolated) // 2]
    assert mid.position.x > path[0].position.x
    assert mid.position.x < path[-1].position.x
    assert mid.position.y > 0.0

    plot_path = tmp_path / "interpolation_3_points_7_segments.png"
    _save_xy_plot(interpolated, plot_path, "Interpolated path with 3 control points and 7 segments", path)
    assert plot_path.exists()
