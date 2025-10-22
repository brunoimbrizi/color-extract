"""
Utility functions for color extraction and manipulation.
"""

import numpy as np
from PIL import Image
import sys


def load_and_prepare_image(image_path, max_dimension=64):
    """
    Load image and convert to RGB array, downscaling for performance.

    Args:
        image_path: Path to the input image
        max_dimension: Maximum dimension for downscaling (default: 64)

    Returns:
        Tuple of (original PIL Image, downscaled numpy array)
    """
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')

        # Keep original for display
        original = img.copy()

        # Downscale if too large
        width, height = img.size
        if max(width, height) > max_dimension:
            ratio = max_dimension / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            # print(f"Downscaled image from {width}x{height} to {img.size[0]}x{img.size[1]}")

        return original, np.array(img)
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)


def rgb_to_hex(rgb):
    """
    Convert RGB tuple to hex color string.

    Args:
        rgb: Tuple or list of RGB values (0-255)

    Returns:
        Hex color string (e.g., '#ff0000')
    """
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def hex_to_rgb(hex_color):
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., '#ff0000')

    Returns:
        Tuple of RGB values (0-255)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def sort_colors_by_spatial_position(img_array, colors, axis='x'):
    """
    Sort colors based on where they appear spatially in the image.

    This function analyzes where each color predominantly appears in the image
    and sorts them based on their average position along the specified axis.

    Args:
        img_array: The image as numpy array (height, width, 3)
        colors: List of RGB colors from clustering
        axis: 'x' for left-to-right, 'y' for top-to-bottom

    Returns:
        List of colors sorted by spatial position
    """
    height, width, _ = img_array.shape
    pixels = img_array.reshape(-1, 3).astype(np.float32)

    # Create coordinate arrays
    y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    x_coords_flat = x_coords.flatten()
    y_coords_flat = y_coords.flatten()

    # For each color, find which pixels are closest to it
    color_positions = []

    for color in colors:
        # Calculate distance from each pixel to this color
        distances = np.sqrt(np.sum((pixels - color) ** 2, axis=1))

        # Find pixels that are closest to this color (within a threshold)
        threshold = np.percentile(distances, 10)
        mask = distances <= threshold

        if np.sum(mask) > 0:
            if axis == 'x':
                avg_position = np.mean(x_coords_flat[mask])
            else:
                avg_position = np.mean(y_coords_flat[mask])
        else:
            avg_position = width / 2 if axis == 'x' else height / 2

        color_positions.append((color, avg_position))

    # Sort by position
    color_positions.sort(key=lambda x: x[1])
    sorted_colors = [color for color, pos in color_positions]

    return sorted_colors


def calculate_color_statistics(img_array, colors):
    """
    Calculate statistics for extracted colors.

    Args:
        img_array: Image as numpy array (H, W, 3)
        colors: List of RGB color tuples

    Returns:
        List of dicts with 'hex' and 'percentage' for each color
    """
    pixels = img_array.reshape(-1, 3).astype(np.float32)
    total_pixels = len(pixels)
    stats = []

    for color in colors:
        # Convert color to numpy array if needed
        color_array = np.array(color, dtype=np.float32)

        # Calculate distance from each pixel to this color
        distances = np.sqrt(np.sum((pixels - color_array) ** 2, axis=1))

        # Store color info and distances for processing
        stats.append({
            'hex': rgb_to_hex(color),
            'percentage': 0,  # Will be calculated next
            'distances': distances
        })

    # Assign each pixel to its closest color
    all_distances = np.array([stat['distances'] for stat in stats])
    closest_color_indices = np.argmin(all_distances, axis=0)

    # Count pixels for each color
    for i, stat in enumerate(stats):
        count = int(np.sum(closest_color_indices == i))
        stat['percentage'] = float(round((count / total_pixels) * 100, 1))
        del stat['distances']  # Remove temporary data

    return stats


def normalize_image_array(image_array, input_range=(0, 1), output_range=(0, 255)):
    """
    Normalize image array from one range to another.
    Useful for converting between different color value ranges.

    Args:
        image_array: numpy array of image data
        input_range: Tuple of (min, max) for input range
        output_range: Tuple of (min, max) for output range

    Returns:
        Normalized numpy array
    """
    in_min, in_max = input_range
    out_min, out_max = output_range

    # Normalize to 0-1
    normalized = (image_array - in_min) / (in_max - in_min)

    # Scale to output range
    scaled = normalized * (out_max - out_min) + out_min

    return scaled.astype(np.uint8) if output_range == (0, 255) else scaled
