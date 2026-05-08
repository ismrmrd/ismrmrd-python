"""Utility functions for working with ISMRMRD data structures."""

import numpy as np


def sign_of_directions(read_dir, phase_dir, slice_dir):
    """Return +1 if the rotation matrix formed by the three direction cosines
    has a non-negative determinant, -1 otherwise.

    Parameters correspond to the ``read_dir``, ``phase_dir``, and
    ``slice_dir`` fields of :class:`~ismrmrd.AcquisitionHeader` /
    :class:`~ismrmrd.ImageHeader`.
    """
    R = np.column_stack([
        np.asarray(read_dir, dtype=np.float64),
        np.asarray(phase_dir, dtype=np.float64),
        np.asarray(slice_dir, dtype=np.float64),
    ])
    return 1 if np.linalg.det(R) >= 0 else -1


def directions_to_quaternion(read_dir, phase_dir, slice_dir):
    """Convert direction cosines to a normalized quaternion ``[a, b, c, d]``.

    Uses the same algorithm as the C library (Princeton quat FAQ Q55).
    The sign of the rotation is checked first; if negative the slice
    direction is flipped before computing the quaternion.
    """
    r = np.asarray(read_dir, dtype=np.float64)
    p = np.asarray(phase_dir, dtype=np.float64)
    s = np.asarray(slice_dir, dtype=np.float64)

    if sign_of_directions(r, p, s) < 0:
        s = -s

    r11, r21, r31 = r
    r12, r22, r32 = p
    r13, r23, r33 = s

    trace = 1.0 + r11 + r22 + r33
    if trace > 1e-5:
        sv = np.sqrt(trace) * 2
        a = (r32 - r23) / sv
        b = (r13 - r31) / sv
        c = (r21 - r12) / sv
        d = 0.25 * sv
    else:
        xd = 1.0 + r11 - r22 - r33
        yd = 1.0 + r22 - r11 - r33
        zd = 1.0 + r33 - r11 - r22
        if xd > 1.0:
            sv = 2.0 * np.sqrt(xd)
            a = 0.25 * sv
            b = (r21 + r12) / sv
            c = (r31 + r13) / sv
            d = (r32 - r23) / sv
        elif yd > 1.0:
            sv = 2.0 * np.sqrt(yd)
            a = (r21 + r12) / sv
            b = 0.25 * sv
            c = (r32 + r23) / sv
            d = (r13 - r31) / sv
        else:
            sv = 2.0 * np.sqrt(zd)
            a = (r13 + r31) / sv
            b = (r23 + r32) / sv
            c = 0.25 * sv
            d = (r21 - r12) / sv
        if a < 0.0:
            a, b, c, d = -a, -b, -c, -d

    return np.array([a, b, c, d], dtype=np.float32)


def quaternion_to_directions(quat):
    """Convert a normalized quaternion ``[a, b, c, d]`` to direction cosines.

    Returns ``(read_dir, phase_dir, slice_dir)`` as three float32 arrays of
    length 3 (Princeton quat FAQ Q54).
    """
    a, b, c, d = (float(x) for x in quat)

    read_dir  = np.array([1 - 2*(b*b + c*c),  2*(a*b + c*d),      2*(a*c - b*d)],      dtype=np.float32)
    phase_dir = np.array([2*(a*b - c*d),       1 - 2*(a*a + c*c),  2*(b*c + a*d)],      dtype=np.float32)
    slice_dir = np.array([2*(a*c + b*d),       2*(b*c - a*d),      1 - 2*(a*a + b*b)],  dtype=np.float32)

    return read_dir, phase_dir, slice_dir
