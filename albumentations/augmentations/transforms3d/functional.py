import random
from typing import Literal

import numpy as np

from albumentations.core.types import NUM_VOLUME_DIMENSIONS, ColorType


def adjust_padding_by_position3d(
    paddings: list[tuple[int, int]],  # [(front, back), (top, bottom), (left, right)]
    position: Literal["center", "random"],
    py_random: random.Random,
) -> tuple[int, int, int, int, int, int]:
    """Adjust padding values based on desired position for 3D data.

    Args:
        paddings: List of tuples containing padding pairs for each dimension [(d_pad), (h_pad), (w_pad)]
        position: Position of the image after padding. Either 'center' or 'random'
        py_random: Random number generator

    Returns:
        tuple[int, int, int, int, int, int]: Final padding values (d_front, d_back, h_top, h_bottom, w_left, w_right)
    """
    if position == "center":
        return (
            paddings[0][0],  # d_front
            paddings[0][1],  # d_back
            paddings[1][0],  # h_top
            paddings[1][1],  # h_bottom
            paddings[2][0],  # w_left
            paddings[2][1],  # w_right
        )

    # For random position, redistribute padding for each dimension
    d_pad = sum(paddings[0])
    h_pad = sum(paddings[1])
    w_pad = sum(paddings[2])

    return (
        py_random.randint(0, d_pad),  # d_front
        d_pad - py_random.randint(0, d_pad),  # d_back
        py_random.randint(0, h_pad),  # h_top
        h_pad - py_random.randint(0, h_pad),  # h_bottom
        py_random.randint(0, w_pad),  # w_left
        w_pad - py_random.randint(0, w_pad),  # w_right
    )


def pad_3d_with_params(
    volume: np.ndarray,
    padding: tuple[int, int, int, int, int, int],  # (d_front, d_back, h_top, h_bottom, w_left, w_right)
    value: ColorType,
) -> np.ndarray:
    """Pad 3D image with given parameters.

    Args:
        volume: Input volume with shape (depth, height, width) or (depth, height, width, channels)
        padding: Padding values (d_front, d_back, h_top, h_bottom, w_left, w_right)
        value: Padding value

    Returns:
        Padded image with same number of dimensions as input
    """
    d_front, d_back, h_top, h_bottom, w_left, w_right = padding

    # Skip if no padding is needed
    if d_front == d_back == h_top == h_bottom == w_left == w_right == 0:
        return volume

    # Handle both 3D and 4D arrays
    pad_width = [
        (d_front, d_back),  # depth padding
        (h_top, h_bottom),  # height padding
        (w_left, w_right),  # width padding
    ]

    # Add channel padding if 4D array
    if volume.ndim == NUM_VOLUME_DIMENSIONS:
        pad_width.append((0, 0))  # no padding for channels

    return np.pad(
        volume,
        pad_width=pad_width,
        mode="constant",
        constant_values=value,
    )


def crop3d(
    volume: np.ndarray,
    crop_coords: tuple[int, int, int, int, int, int],
) -> np.ndarray:
    """Crop 3D volume using coordinates.

    Args:
        volume: Input volume with shape (z, y, x) or (z, y, x, channels)
        crop_coords: Tuple of (z_min, z_max, y_min, y_max, x_min, x_max) coordinates for cropping

    Returns:
        Cropped volume with same number of dimensions as input
    """
    z_min, z_max, y_min, y_max, x_min, x_max = crop_coords

    return volume[z_min:z_max, y_min:y_max, x_min:x_max]


def cutout3d(volume: np.ndarray, holes: np.ndarray, fill_value: ColorType) -> np.ndarray:
    """Cut out holes in 3D volume and fill them with a given value."""
    volume = volume.copy()
    for z1, y1, x1, z2, y2, x2 in holes:
        volume[z1:z2, y1:y2, x1:x2] = fill_value
    return volume
