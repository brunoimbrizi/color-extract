"""
Color Extractor - Extract dominant colors from images using various K-Means clustering approaches.

A comprehensive toolkit for color extraction with support for multiple algorithms,
spatial color sorting, and both CLI and programmatic usage.
"""

__version__ = '0.0.2'
__author__ = 'Bruno Imbrizi'
__email__ = 'your.email@example.com'

# Import core extraction functions
from .core import (
    extract_colors_kmeans_original,
    extract_colors_weighted_aggressive,
    extract_colors_vibrant_separate,
    extract_colors_lab_enhanced,
    extract_colors_multistage,
    EXTRACTION_METHODS
)

# Import utility functions
from .utils import (
    load_and_prepare_image,
    rgb_to_hex,
    hex_to_rgb,
    sort_colors_by_spatial_position,
    calculate_color_statistics,
    normalize_image_array
)

# Import visualization functions
from .visualization import (
    plot_single_result,
    plot_comparison,
    print_color_results,
    create_color_palette_image
)

# Main convenience function for easy API usage
def extract_colors(image, method='lab', n_colors=6, sort_by='x-axis'):
    """
    Extract dominant colors from an image.

    Args:
        image: Either a file path (string) or a numpy array (H, W, 3) with RGB values 0-255
        method: Extraction method - 'kmeans', 'aggressive', 'vibrant', 'lab', or 'multistage'
        n_colors: Number of colors to extract
        sort_by: How to sort colors - 'x-axis', 'y-axis', or 'frequency'

    Returns:
        List of RGB color tuples

    Example:
        >>> import color_extract
        >>> colors = color_extract.extract_colors('image.jpg', method='lab', n_colors=5)
        >>> for color in colors:
        ...     print(color_extract.rgb_to_hex(color))
    """
    import numpy as np

    # Handle input
    if isinstance(image, str):
        # Load from file path
        _, img_array = load_and_prepare_image(image)
    elif isinstance(image, np.ndarray):
        # Use numpy array directly
        img_array = image
    else:
        raise ValueError("Image must be either a file path or numpy array")

    # Get extraction function
    if method not in EXTRACTION_METHODS:
        raise ValueError(f"Unknown method: {method}. Available: {list(EXTRACTION_METHODS.keys())}")

    _, extraction_func = EXTRACTION_METHODS[method]

    # Extract colors
    colors = extraction_func(img_array, n_colors)

    # Sort colors if requested
    if sort_by == 'x-axis':
        colors = sort_colors_by_spatial_position(img_array, colors, axis='x')
    elif sort_by == 'y-axis':
        colors = sort_colors_by_spatial_position(img_array, colors, axis='y')
    elif sort_by == 'frequency':
        pass  # Already sorted by frequency from extraction

    # Return colors
    return colors


# List all public functions and classes
__all__ = [
    # Main API
    'extract_colors',

    # Core extraction functions
    'extract_colors_kmeans_original',
    'extract_colors_weighted_aggressive',
    'extract_colors_vibrant_separate',
    'extract_colors_lab_enhanced',
    'extract_colors_multistage',
    'EXTRACTION_METHODS',

    # Utilities
    'load_and_prepare_image',
    'rgb_to_hex',
    'hex_to_rgb',
    'sort_colors_by_spatial_position',
    'calculate_color_statistics',
    'normalize_image_array',

    # Visualization
    'plot_single_result',
    'plot_comparison',
    'print_color_results',
    'create_color_palette_image',
]
