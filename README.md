# Color Extract

[![PyPI version](https://badge.fury.io/py/color-extract.svg)](https://badge.fury.io/py/color-extract)
[![Python Support](https://img.shields.io/pypi/pyversions/color-extract.svg)](https://pypi.org/project/color-extract/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A toolkit to extract dominant colors from images using various K-Means clustering approaches.

| Example A | Example B | Example C |
| --- | --- | --- |
| <img src="./output/palette_Additional_073_all_6.png" width=300> | <img src="./output/palette_OilDrums_all_6.png" width=300> | <img src="./output/palette_Additional_847_all_6.png" width=300> |


## Features

**Extraction Methods**
- **Original K-Means**: Standard clustering approach
- **LAB Enhanced**: Perceptually uniform color space (default)
- **Aggressive Weighting**: Emphasizes vibrant colors
- **Vibrant Separate**: Separate clustering for vibrant and base colors
- **Multi-stage**: Extract vibrant colors first, then distinct base colors

**Sorting**
- Spatial sorting (left-to-right or top-to-bottom)
- Frequency-based sorting

## Installation

```bash
pip install color-extract
```

## Command Line Usage

Basic extraction with default settings:
```bash
color-extract image.jpg
```

Extract 8 colors using the vibrant method:
```bash
color-extract image.jpg --colors 8 --method vibrant
```

Compare all methods:
```bash
color-extract image.jpg --method all --output comparison.png
```

## CLI Options

```
usage:
  color-extract [options] image

Arguments:
  image                Path to the input image

Options:
  -h, --help           Show help message
  --colors, -c         Number of colors to extract (default: 6)
  --method, -m         Extraction method (default: lab)
  --output, -o         Output file path
  --no-plot            Disable plot generation (console output only)
  --sort               Color sorting: (default: x-axis)
  --max-dimension      Max dimension for downscaling (default: 64)
  --dpi                DPI for output plots (default: 150)
```

## Python API Usage

```python
import color_extract
import numpy as np
from PIL import Image

# Simple extraction from file
colors = color_extract.extract_colors('image.jpg', method='lab', n_colors=5)
for color in colors:
    print(color_extract.rgb_to_hex(color))

# Use with numpy array
img = Image.open('image.jpg')
img_array = np.array(img)
colors = color_extract.extract_colors(img_array, method='aggressive')

# Advanced usage with visualization
from color_extract import plot_single_result, load_and_prepare_image

img, img_array = load_and_prepare_image('image.jpg')
colors = color_extract.extract_colors_lab_enhanced(img_array, n_colors=6)
sorted_colors = color_extract.sort_colors_by_spatial_position(img_array, colors)

# Generate visualization
plot_single_result(img, img_array, sorted_colors, 'LAB Enhanced', 'output.png')
```

## TouchDesigner Integration

```python
# In TouchDesigner, use with TOP operators
import color_extract

def extract_from_top(top):
    # Get pixels from TOP (TouchDesigner returns 0-1 range)
    pixels = top.numpyArray(delayed=True)

    # Convert to 0-255 range
    img_array = color_extract.normalize_image_array(
        pixels,
        input_range=(0, 1),
        output_range=(0, 255)
    )

    # Extract colors
    colors = color_extract.extract_colors(img_array, method='lab')

    # Convert to hex for use in TouchDesigner
    hex_colors = [color_extract.rgb_to_hex(c) for c in colors]

    return hex_colors
```

## API Reference

### Main Functions

#### `extract_colors(image, method='lab', n_colors=6, sort_by='x-axis')`

Main convenience function for color extraction.

**Parameters:**
- `image`: File path (str) or numpy array (H, W, 3)
- `method`: Extraction method name
- `n_colors`: Number of colors to extract
- `sort_by`: Sorting method ('x-axis', 'y-axis', 'frequency')

**Returns:**
- List of RGB tuples

### Individual Extraction Methods

Each method can be used directly for more control:

```python
# Original K-Means
colors = extract_colors_kmeans_original(img_array, n_colors=6)

# LAB color space
colors = extract_colors_lab_enhanced(img_array, n_colors=6, saturation_boost=5.0)

# Aggressive saturation weighting
colors = extract_colors_weighted_aggressive(img_array, n_colors=6, saturation_boost=10.0)

# Separate vibrant colors
colors = extract_colors_vibrant_separate(img_array, n_colors=6, n_vibrant=3)

# Multi-stage extraction
colors = extract_colors_multistage(img_array, n_colors=6)
```

### Utility Functions

```python
# Color conversion
hex_color = rgb_to_hex((255, 128, 0))  # Returns '#ff8000'
rgb = hex_to_rgb('#ff8000')  # Returns (255, 128, 0)

# Spatial sorting
sorted_colors = sort_colors_by_spatial_position(img_array, colors, axis='x')

# Calculate statistics
stats = calculate_color_statistics(img_array, colors)

# Normalize arrays (useful for TouchDesigner)
normalized = normalize_image_array(array, input_range=(0, 1), output_range=(0, 255))
```

### Visualization Functions

```python
# Plot single result
fig = plot_single_result(img, img_array, colors, 'Method Name', 'output.png')

# Compare multiple methods
algorithms_dict = {
    'Method 1': colors1,
    'Method 2': colors2
}
fig = plot_comparison(img, img_array, algorithms_dict, 'comparison.png')

# Create simple palette image
palette_array = create_color_palette_image(colors, width=100, height=100)
```


## Further Reading

* [New Approach to Dominant and Prominent Color Extraction in Images with a Wide Range of Hues](https://www.mdpi.com/2227-7080/13/6/230)
* [Dominant Colors with (not just) K-Means](https://tatasz.github.io/dominant_colors/)
