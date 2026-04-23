from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from robot_interface.interface.arm import CartesianPosition, Orientation


def _normalize_model_name(model: str) -> str:
    normalized_model = model.strip().lower()
    if normalized_model not in {"ur10", "ur10e"}:
        raise ValueError("model must be 'ur10' or 'ur10e'")
    return normalized_model


def _get_robot_parameters(model: str) -> Dict[str, float]:
    normalized_model = _normalize_model_name(model)

    if normalized_model == "ur10":
        return {
            "d1": 0.1273,
            "a2": -0.6120,
            "a3": -0.5723,
            "d4": 0.163941,
            "d5": 0.1157,
            "d6": 0.0922,
        }

    return {
        "d1": 0.1273,
        "a2": -0.6127,
        "a3": -0.57155,
        "d4": 0.17415,
        "d5": 0.11985,
        "d6": 0.11655,
    }


def _base_transform(base_offset: Optional[CartesianPosition] = None) -> np.ndarray:
    transform_matrix = np.eye(4, dtype=float)

    if base_offset is None:
        return transform_matrix

    transform_matrix[0, 3] = base_offset.x / 1000.0
    transform_matrix[1, 3] = base_offset.y / 1000.0
    transform_matrix[2, 3] = base_offset.z / 1000.0
    return transform_matrix


def _dh_transform(
    theta_radians: float,
    d_meters: float,
    a_meters: float,
    alpha_radians: float,
) -> np.ndarray:
    cosine_theta = np.cos(theta_radians)
    sine_theta = np.sin(theta_radians)
    cosine_alpha = np.cos(alpha_radians)
    sine_alpha = np.sin(alpha_radians)

    return np.array(
        [
            [
                cosine_theta,
                -sine_theta * cosine_alpha,
                sine_theta * sine_alpha,
                a_meters * cosine_theta,
            ],
            [
                sine_theta,
                cosine_theta * cosine_alpha,
                -cosine_theta * sine_alpha,
                a_meters * sine_theta,
            ],
            [
                0.0,
                sine_alpha,
                cosine_alpha,
                d_meters,
            ],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def _rotation_matrix_to_rotation_vector(rotation_matrix: np.ndarray) -> np.ndarray:
    trace_value = float(np.trace(rotation_matrix))
    cosine_theta = (trace_value - 1.0) / 2.0
    cosine_theta = float(np.clip(cosine_theta, -1.0, 1.0))
    theta_value = float(np.arccos(cosine_theta))

    if np.isclose(theta_value, 0.0):
        return np.zeros(3, dtype=float)

    sine_theta = np.sin(theta_value)

    if np.isclose(sine_theta, 0.0):
        eigenvalues, eigenvectors = np.linalg.eig(rotation_matrix)
        closest_index = int(np.argmin(np.abs(eigenvalues - 1.0)))
        axis_vector = np.real(eigenvectors[:, closest_index])
        axis_vector = axis_vector / np.linalg.norm(axis_vector)
        return axis_vector * theta_value

    axis_vector = np.array(
        [
            rotation_matrix[2, 1] - rotation_matrix[1, 2],
            rotation_matrix[0, 2] - rotation_matrix[2, 0],
            rotation_matrix[1, 0] - rotation_matrix[0, 1],
        ],
        dtype=float,
    ) / (2.0 * sine_theta)

    return axis_vector * theta_value


def _rotation_vector_to_rotation_matrix(rotation_vector: np.ndarray) -> np.ndarray:
    theta_value = float(np.linalg.norm(rotation_vector))

    if np.isclose(theta_value, 0.0):
        return np.eye(3, dtype=float)

    axis_vector = rotation_vector / theta_value
    axis_x, axis_y, axis_z = axis_vector

    skew_matrix = np.array(
        [
            [0.0, -axis_z, axis_y],
            [axis_z, 0.0, -axis_x],
            [-axis_y, axis_x, 0.0],
        ],
        dtype=float,
    )

    identity_matrix = np.eye(3, dtype=float)

    return (
        identity_matrix
        + np.sin(theta_value) * skew_matrix
        + (1.0 - np.cos(theta_value)) * (skew_matrix @ skew_matrix)
    )


def _build_target_transform(
    target_position: CartesianPosition,
    target_orientation: Orientation,
) -> np.ndarray:
    target_transform = np.eye(4, dtype=float)
    target_transform[0:3, 0:3] = _rotation_vector_to_rotation_matrix(
        np.array(
            [target_orientation.rx, target_orientation.ry, target_orientation.rz],
            dtype=float,
        )
    )
    target_transform[0:3, 3] = np.array(
        [
            target_position.x / 1000.0,
            target_position.y / 1000.0,
            target_position.z / 1000.0,
        ],
        dtype=float,
    )
    return target_transform


def _pose_error(current_transform: np.ndarray, target_transform: np.ndarray) -> np.ndarray:
    current_position = current_transform[0:3, 3]
    target_position = target_transform[0:3, 3]
    position_error = target_position - current_position

    current_rotation = current_transform[0:3, 0:3]
    target_rotation = target_transform[0:3, 0:3]
    relative_rotation = current_rotation.T @ target_rotation
    orientation_error = _rotation_matrix_to_rotation_vector(relative_rotation)

    return np.concatenate([position_error, orientation_error])


def _ur_forward_transform(
    joint_angles: List[float],
    model: str,
    base_offset: Optional[CartesianPosition] = None,
) -> np.ndarray:
    if len(joint_angles) != 6:
        raise ValueError("joint_angles must contain exactly 6 values")

    parameters = _get_robot_parameters(model)

    q1, q2, q3, q4, q5, q6 = joint_angles

    d1 = parameters["d1"]
    a2 = parameters["a2"]
    a3 = parameters["a3"]
    d4 = parameters["d4"]
    d5 = parameters["d5"]
    d6 = parameters["d6"]

    transform_01 = _dh_transform(q1, d1, 0.0, np.pi / 2.0)
    transform_12 = _dh_transform(q2, 0.0, a2, 0.0)
    transform_23 = _dh_transform(q3, 0.0, a3, 0.0)
    transform_34 = _dh_transform(q4, d4, 0.0, np.pi / 2.0)
    transform_45 = _dh_transform(q5, d5, 0.0, -np.pi / 2.0)
    transform_56 = _dh_transform(q6, d6, 0.0, 0.0)

    robot_transform = (
        transform_01
        @ transform_12
        @ transform_23
        @ transform_34
        @ transform_45
        @ transform_56
    )

    return _base_transform(base_offset) @ robot_transform


def forward_kinematics(
    joint_angles: List[float],
    model: str,
    base_offset: Optional[CartesianPosition] = None,
) -> Tuple[CartesianPosition, Orientation]:
    """
    Compute forward kinematics for UR10 or UR10e.

    Args:
        joint_angles:
            Six joint angles in radians.
        model:
            'ur10' or 'ur10e'
        base_offset:
            Optional fixed base translation in mm.

    Returns:
        Tuple[CartesianPosition, Orientation]
        Position is in mm.
        Orientation is a rotation vector in rad.
    """
    transform_matrix = _ur_forward_transform(
        joint_angles=joint_angles,
        model=model,
        base_offset=base_offset,
    )

    position_meters = transform_matrix[0:3, 3]
    rotation_matrix = transform_matrix[0:3, 0:3]
    rotation_vector = _rotation_matrix_to_rotation_vector(rotation_matrix)

    cartesian_position = CartesianPosition(
        x=float(position_meters[0] * 1000.0),
        y=float(position_meters[1] * 1000.0),
        z=float(position_meters[2] * 1000.0),
    )

    orientation = Orientation(
        rx=float(rotation_vector[0]),
        ry=float(rotation_vector[1]),
        rz=float(rotation_vector[2]),
    )

    return cartesian_position, orientation


def inverse_kinematics(
    target_position: CartesianPosition,
    target_orientation: Orientation,
    model: str,
    base_offset: Optional[CartesianPosition] = None,
    initial_guess: Optional[List[float]] = None,
    max_iterations: int = 200,
    tolerance: float = 1e-6,
) -> List[float]:
    """
    Numerical inverse kinematics for UR10 or UR10e.

    Args:
        target_position:
            Cartesian target in mm.
        target_orientation:
            Rotation vector target in rad.
        model:
            'ur10' or 'ur10e'
        base_offset:
            Optional fixed base translation in mm.
        initial_guess:
            Optional starting joint configuration in radians.
        max_iterations:
            Maximum optimization iterations.
        tolerance:
            Convergence threshold on pose error.

    Returns:
        List[float]:
            Six joint angles in radians.

    Notes:
        This is a local numerical solver, not a closed-form UR solver.
        A good initial guess helps a lot.
    """
    _normalize_model_name(model)

    if initial_guess is None:
        joint_vector = np.zeros(6, dtype=float)
    else:
        if len(initial_guess) != 6:
            raise ValueError("initial_guess must contain exactly 6 values")
        joint_vector = np.array(initial_guess, dtype=float)

    target_transform = _build_target_transform(target_position, target_orientation)

    damping_value = 1e-4
    finite_difference_step = 1e-6

    for _ in range(max_iterations):
        current_transform = _ur_forward_transform(
            joint_vector.tolist(),
            model,
            base_offset=base_offset,
        )
        error_vector = _pose_error(current_transform, target_transform)

        if np.linalg.norm(error_vector) < tolerance:
            return joint_vector.tolist()

        jacobian_matrix = np.zeros((6, 6), dtype=float)

        for joint_index in range(6):
            perturbed_joint_vector = joint_vector.copy()
            perturbed_joint_vector[joint_index] += finite_difference_step

            perturbed_transform = _ur_forward_transform(
                perturbed_joint_vector.tolist(),
                model,
                base_offset=base_offset,
            )
            perturbed_error_vector = _pose_error(perturbed_transform, target_transform)

            jacobian_matrix[:, joint_index] = (
                perturbed_error_vector - error_vector
            ) / finite_difference_step

        normal_matrix = (
            jacobian_matrix.T @ jacobian_matrix
            + damping_value * np.eye(6, dtype=float)
        )
        right_hand_side = jacobian_matrix.T @ error_vector
        joint_update = np.linalg.solve(normal_matrix, right_hand_side)

        joint_vector += joint_update
        joint_vector = (joint_vector + np.pi) % (2.0 * np.pi) - np.pi

    raise RuntimeError(
        f"Inverse kinematics did not converge for model '{model}'."
    )


if __name__ == "__main__":
    sample_joint_angles = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
    sample_base_offset = CartesianPosition(x=0.0, y=0.0, z=53.0)

    for robot_model in ["ur10", "ur10e"]:
        print(f"\nModel: {robot_model}")

        forward_position, forward_orientation = forward_kinematics(
            sample_joint_angles,
            robot_model,
            base_offset=sample_base_offset,
        )
        print("Forward position:", forward_position)
        print("Forward orientation:", forward_orientation)

        recovered_joint_angles = inverse_kinematics(
            target_position=forward_position,
            target_orientation=forward_orientation,
            model=robot_model,
            base_offset=sample_base_offset,
            initial_guess=sample_joint_angles,
        )
        print("Recovered joints:", recovered_joint_angles)
