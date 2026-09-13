import numpy as np
import pyvista as pv


def _skew(v):
    """The skew-symmetric cross-product matrix of vector v."""
    return np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0],
    ])


def _flip_matrix(a):
    """A 180-degree rotation matrix, for when a and b point exactly opposite."""
    perp = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    axis = np.cross(a, perp)
    axis /= np.linalg.norm(axis)
    K = _skew(axis)
    return np.eye(3) + 2 * (K @ K)


def rotation_matrix_from_vectors(a, b):
    """Rotation matrix that rotates unit vector a onto unit vector b
    (Rodrigues' rotation formula)."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    s = np.linalg.norm(v)
    c = np.dot(a, b)
    if s < 1e-8:
        return np.eye(3) if c > 0 else _flip_matrix(a)
    K = _skew(v)
    return np.eye(3) + K + K @ K * ((1 - c) / (s ** 2))


def build_rocket_mesh(body_radius=0.04, body_length=0.7, nose_length=0.15,
                       fin_count=3, fin_height=0.08, fin_width=0.12, fin_thickness=0.004):
    """A simple rocket mesh (nose cone + body cylinder + fins), pointing
    along +z with its tail at z=0 and nose tip at z=body_length+nose_length."""
    body = pv.Cylinder(
        center=(0, 0, body_length / 2), direction=(0, 0, 1),
        radius=body_radius, height=body_length,
    )
    nose = pv.Cone(
        center=(0, 0, body_length + nose_length / 2), direction=(0, 0, 1),
        radius=body_radius, height=nose_length,
    )

    rocket = body + nose
    for i in range(fin_count):
        angle = 360.0 / fin_count * i
        fin = pv.Box(bounds=(
            body_radius, body_radius + fin_height,
            -fin_thickness / 2, fin_thickness / 2,
            0, fin_width,
        ))
        fin = fin.rotate_z(angle, point=(0, 0, 0))
        rocket = rocket + fin

    return rocket


def place_rocket(base_mesh, position, direction):
    """A copy of base_mesh rotated to point along `direction` and moved to `position`."""
    z_axis = np.array([0.0, 0.0, 1.0])
    R = rotation_matrix_from_vectors(z_axis, direction)

    matrix = np.eye(4)
    matrix[:3, :3] = R
    matrix[:3, 3] = position

    mesh = base_mesh.copy()
    mesh.transform(matrix, inplace=True)
    return mesh
