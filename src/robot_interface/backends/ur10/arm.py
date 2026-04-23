"""Minimal UR10 arm adapters."""

from __future__ import annotations

import socket
import time
from typing import Any, Sequence

import arklog

from robot_interface.backends.ur10.connection import RemoteModeError
from robot_interface.backends.ur10.kinematics import forward_kinematics, inverse_kinematics
from robot_interface.interface.arm import ArmAdapter, CartesianPose, CartesianPosition, Orientation
from robot_interface.interface.capabilities import ArmCapabilities


def _pose_to_list(pose: CartesianPose) -> list[float]:
    # UR moveL expects position in meters; public API uses millimeters.
    return [
        pose.position.x / 1000.0,
        pose.position.y / 1000.0,
        pose.position.z / 1000.0,
        pose.orientation.rx,
        pose.orientation.ry,
        pose.orientation.rz,
    ]


class UR10RTDEArmAdapter(ArmAdapter):
    backend_name = "ur10_rtde"

    def __init__(self, *, robot_ip: str, rtde_port: int = 30004) -> None:
        self.robot_ip = robot_ip
        self.rtde_port = rtde_port
        self._rtde_ctrl: Any | None = None
        self._rtde_recv: Any | None = None

    def __enter__(self) -> "UR10RTDEArmAdapter":
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.disconnect()

    def get_capabilities(self) -> ArmCapabilities:
        return ArmCapabilities(
            move_cartesian=True,
            raw_command=False,
            wait_for_motion_complete=False,
            kinematics_strategy="adapter",
            cartesian_execution_mode="native",
        )

    def connect(self) -> None:
        try:
            import rtde_control
            import rtde_receive
        except Exception as exc:
            raise RemoteModeError("Could not import ur-rtde modules. Install with: pip install ur-rtde") from exc
        try:
            try:
                self._rtde_ctrl = rtde_control.RTDEControlInterface(self.robot_ip, port=self.rtde_port)
            except TypeError:
                self._rtde_ctrl = rtde_control.RTDEControlInterface(self.robot_ip)
            try:
                self._rtde_recv = rtde_receive.RTDEReceiveInterface(self.robot_ip, port=self.rtde_port)
            except TypeError:
                self._rtde_recv = rtde_receive.RTDEReceiveInterface(self.robot_ip)
        except Exception as exc:
            raise RemoteModeError(f"Failed to connect RTDE at {self.robot_ip}: {exc}") from exc

    def disconnect(self) -> None:
        if self._rtde_ctrl is not None:
            try:
                self._rtde_ctrl.disconnect()
            except Exception:
                pass
        if self._rtde_recv is not None:
            try:
                self._rtde_recv.disconnect()
            except Exception:
                pass
        self._rtde_ctrl = None
        self._rtde_recv = None

    def _require_ctrl(self) -> Any:
        if self._rtde_ctrl is None:
            raise RemoteModeError("RTDE control is not connected")
        return self._rtde_ctrl

    def _require_recv(self) -> Any:
        if self._rtde_recv is None:
            raise RemoteModeError("RTDE receive is not connected")
        return self._rtde_recv

    def _rtde_diagnostics(self) -> str:
        recv = self._require_recv()
        fields: list[str] = []
        probes = [
            ("robot_mode", "getRobotMode"),
            ("safety_mode", "getSafetyMode"),
            ("safety_status_bits", "getSafetyStatusBits"),
            ("robot_status_bits", "getRobotStatus"),
            ("runtime_state", "getRuntimeState"),
            ("speed_scaling", "getSpeedScaling"),
            ("is_protective_stopped", "isProtectiveStopped"),
            ("is_emergency_stopped", "isEmergencyStopped"),
            ("is_program_running", "isProgramRunning"),
        ]
        for label, method_name in probes:
            method = getattr(recv, method_name, None)
            if callable(method):
                try:
                    fields.append(f"{label}={method()}")
                except Exception:
                    fields.append(f"{label}=<error>")
        return ", ".join(fields) if fields else "no diagnostics available"

    def _ensure_motion_enabled(self) -> None:
        recv = self._require_recv()
        get_speed_scaling = getattr(recv, "getSpeedScaling", None)
        if callable(get_speed_scaling):
            try:
                scaling = float(get_speed_scaling())
            except Exception:
                return
            if scaling <= 0.0:
                raise RemoteModeError(
                    "Motion is disabled: speed_scaling=0.0. Increase the robot speed slider above 0% and retry."
                )

    def move_joint(self, joints_rad: Sequence[float], *, speed: float, acceleration: float) -> None:
        self._ensure_motion_enabled()
        result = self._require_ctrl().moveJ(list(joints_rad), speed, acceleration)
        if result is False:
            raise RemoteModeError(f"moveJ command was rejected by controller ({self._rtde_diagnostics()})")

    def move_cartesian(self, pose: CartesianPose, *, speed: float, acceleration: float) -> None:
        self._ensure_motion_enabled()
        result = self._require_ctrl().moveL(_pose_to_list(pose), speed, acceleration)
        if result is False:
            raise RemoteModeError(f"moveL command was rejected by controller ({self._rtde_diagnostics()})")

    @property
    def joint_positions(self) -> list[float]:
        return [float(v) for v in self._require_recv().getActualQ()]

    @property
    def cartesian_position(self) -> CartesianPosition:
        recv = self._require_recv()
        if not hasattr(recv, "getActualTCPPose"):
            position, _ = self.forward_kinematics(self.joint_positions)
            return position
        tcp_pose = recv.getActualTCPPose()
        return CartesianPosition(
            x=float(tcp_pose[0]) * 1000.0,
            y=float(tcp_pose[1]) * 1000.0,
            z=float(tcp_pose[2]) * 1000.0,
        )

    @property
    def orientation(self) -> Orientation:
        recv = self._require_recv()
        if not hasattr(recv, "getActualTCPPose"):
            _, orientation = self.forward_kinematics(self.joint_positions)
            return orientation
        tcp_pose = recv.getActualTCPPose()
        return Orientation(
            rx=float(tcp_pose[3]),
            ry=float(tcp_pose[4]),
            rz=float(tcp_pose[5]),
        )

    def stop_motion(self, *, immediate: bool = True) -> None:
        _ = immediate
        ctrl = self._require_ctrl()
        if hasattr(ctrl, "stopJ"):
            ctrl.stopJ(2.0)
        elif hasattr(ctrl, "stopScript"):
            ctrl.stopScript()
        else:
            arklog.warning("RTDE stop command not available; ignoring stop_motion")

    def power_on(self) -> None:
        arklog.warning("RTDE adapter does not implement power_on; ignoring call")

    def brake_release(self) -> None:
        arklog.warning("RTDE adapter does not implement brake_release; ignoring call")

    def run_raw_command(self, command: str, *, unsafe: bool = True) -> str | None:
        _ = command
        if not unsafe:
            raise ValueError("run_raw_command requires unsafe=True")
        arklog.warning("RTDE adapter does not implement raw URScript command execution; ignoring call")
        return None

    def forward_kinematics(self, joints_rad: Sequence[float]) -> tuple[CartesianPosition, Orientation]:
        return forward_kinematics(list(joints_rad), model="ur10e", base_offset=CartesianPosition(x=0.0, y=0.0, z=53.0))

    def inverse_kinematics(
        self,
        *,
        position: Sequence[float],
        orientation: Sequence[Sequence[float]],
        current_joints_rad: Sequence[float] | None = None,
    ) -> list[float]:
        target_position = CartesianPosition(float(position[0]), float(position[1]), float(position[2]))
        target_orientation = Orientation(float(orientation[0][0]), float(orientation[0][1]), float(orientation[0][2]))
        solution = inverse_kinematics(
            target_position=target_position,
            target_orientation=target_orientation,
            model="ur10e",
            base_offset=CartesianPosition(x=0.0, y=0.0, z=53.0),
            initial_guess=list(current_joints_rad) if current_joints_rad is not None else None,
        )
        if solution is None:
            raise RuntimeError("No inverse kinematics solution")
        return [float(v) for v in solution]


class UR10URScriptArmAdapter(ArmAdapter):
    backend_name = "ur10_urscript"

    def __init__(self, *, robot_ip: str, urscript_port: int = 30001, command_delay: float = 0.1) -> None:
        self.robot_ip = robot_ip
        self.urscript_port = urscript_port
        self.command_delay = max(0.0, command_delay)

    def __enter__(self) -> "UR10URScriptArmAdapter":
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.disconnect()

    def get_capabilities(self) -> ArmCapabilities:
        return ArmCapabilities(
            move_cartesian=True,
            raw_command=True,
            wait_for_motion_complete=False,
            kinematics_strategy="adapter",
            cartesian_execution_mode="native",
        )

    def connect(self) -> None:
        try:
            with socket.create_connection((self.robot_ip, self.urscript_port), timeout=2.0):
                pass
        except Exception as exc:
            raise RemoteModeError(f"Failed to connect URScript at {self.robot_ip}:{self.urscript_port}: {exc}") from exc

    def disconnect(self) -> None:
        return None

    def _send_urscript(self, command: str) -> None:
        if not command.endswith("\n"):
            command += "\n"
        try:
            with socket.create_connection((self.robot_ip, self.urscript_port), timeout=2.0) as sock:
                sock.sendall(command.encode("utf-8"))
            if self.command_delay > 0:
                time.sleep(self.command_delay)
        except Exception as exc:
            raise RemoteModeError(f"Failed to send URScript command: {exc}") from exc

    def move_joint(self, joints_rad: Sequence[float], *, speed: float, acceleration: float) -> None:
        self._send_urscript(f"movej({list(joints_rad)}, a={acceleration}, v={speed})")

    def move_cartesian(self, pose: CartesianPose, *, speed: float, acceleration: float) -> None:
        self._send_urscript(f"movel({_pose_to_list(pose)}, a={acceleration}, v={speed})")

    @property
    def joint_positions(self) -> list[float]:
        raise RemoteModeError("joint_positions is not supported in URScript adapter")

    @property
    def cartesian_position(self) -> CartesianPosition:
        position, _ = self.forward_kinematics(self.joint_positions)
        return position

    @property
    def orientation(self) -> Orientation:
        _, orientation = self.forward_kinematics(self.joint_positions)
        return orientation

    def stop_motion(self, *, immediate: bool = True) -> None:
        _ = immediate
        self._send_urscript("stopj(2.0)")

    def power_on(self) -> None:
        arklog.warning("URScript adapter does not implement power_on; ignoring call")

    def brake_release(self) -> None:
        arklog.warning("URScript adapter does not implement brake_release; ignoring call")

    def run_raw_command(self, command: str, *, unsafe: bool = True) -> str | None:
        if not unsafe:
            raise ValueError("run_raw_command requires unsafe=True")
        self._send_urscript(command)
        return command

    def forward_kinematics(self, joints_rad: Sequence[float]) -> tuple[CartesianPosition, Orientation]:
        return forward_kinematics(list(joints_rad), model="ur10e", base_offset=CartesianPosition(x=0.0, y=0.0, z=53.0))

    def inverse_kinematics(
        self,
        *,
        position: Sequence[float],
        orientation: Sequence[Sequence[float]],
        current_joints_rad: Sequence[float] | None = None,
    ) -> list[float]:
        target_position = CartesianPosition(float(position[0]), float(position[1]), float(position[2]))
        target_orientation = Orientation(float(orientation[0][0]), float(orientation[0][1]), float(orientation[0][2]))
        solution = inverse_kinematics(
            target_position=target_position,
            target_orientation=target_orientation,
            model="ur10e",
            base_offset=CartesianPosition(x=0.0, y=0.0, z=53.0),
            initial_guess=list(current_joints_rad) if current_joints_rad is not None else None,
        )
        if solution is None:
            raise RuntimeError("No inverse kinematics solution")
        return [float(v) for v in solution]
