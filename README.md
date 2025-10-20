# Color Extractor

[![PyPI version](https://badge.fury.io/py/color-extractor.svg)](https://badge.fury.io/py/color-extractor)
[![Python Support](https://img.shields.io/pypi/pyversions/color-extractor.svg)](https://pypi.org/project/color-extractor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A toolkit to extract dominant colors from images using various K-Means clustering approaches.

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
- Custom sorting options

## Installation

```bash
pip install color-extractor
```

## Quick Start

### Command Line Usage

Basic extraction with default settings:
```bash
color-extractor image.jpg
```

Extract 8 colors using the vibrant method:
```bash
color-extractor image.jpg --colors 8 --method vibrant
```

Compare all methods:
```bash
color-extractor image.jpg --method all --output comparison.png
```

Advanced options:
```bash
color-extractor image.jpg \
    --colors 6 \
    --method lab \
    --sort spatial-x \
    --output palette.png \
    --dpi 300 \
```

### Python API Usage

```python
import color_extractor
import numpy as np
from PIL import Image

# Simple extraction from file
colors = color_extractor.extract_colors('image.jpg', method='lab', n_colors=5)
for color in colors:
    print(color_extractor.rgb_to_hex(color))

# Use with numpy array
img = Image.open('image.jpg')
img_array = np.array(img)
colors = color_extractor.extract_colors(img_array, method='aggressive')

# Advanced usage with visualization
from color_extractor import plot_single_result, load_and_prepare_image

img, img_array = load_and_prepare_image('image.jpg')
colors = color_extractor.extract_colors_lab_enhanced(img_array, n_colors=6)
sorted_colors = color_extractor.sort_colors_by_spatial_position(img_array, colors)

# Generate visualization
plot_single_result(img, img_array, sorted_colors, 'LAB Enhanced', 'output.png')
```

### TouchDesigner Integration

```python
# In TouchDesigner, use with TOP operators
import color_extractor

def extract_from_top(top):
    # Get pixels from TOP (TouchDesigner returns 0-1 range)
    pixels = top.numpyArray(delayed=True)

    # Convert to 0-255 range
    img_array = color_extractor.normalize_image_array(
        pixels,
        input_range=(0, 1),
        output_range=(0, 255)
    )

    # Extract colors
    colors = color_extractor.extract_colors(img_array, method='lab')

    # Convert to hex for use in TouchDesigner
    hex_colors = [color_extractor.rgb_to_hex(c) for c in colors]

    return hex_colors
```

## Extraction Methods Comparison

| Method | Best For | Characteristics |
|--------|----------|----------------|
| **lab** (default) | General use | Perceptually uniform, balanced results |
| **kmeans** | Fast extraction | Original K-Means, frequency-based |
| **aggressive** | Vibrant images | Emphasizes saturated colors |
| **vibrant** | Mixed content | Separates vibrant and muted colors |
| **multistage** | Complex images | Two-stage extraction for variety |

## API Reference

### Main Functions

#### `extract_colors(image, method='lab', n_colors=6, sort_by='spatial-x')`

Main convenience function for color extraction.

**Parameters:**
- `image`: File path (str) or numpy array (H, W, 3)
- `method`: Extraction method name
- `n_colors`: Number of colors to extract
- `sort_by`: Sorting method ('spatial-x', 'spatial-y', 'frequency', None)

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

## CLI Options

```
usage: color-extractor [-h] [--colors COLORS] [--method METHOD] [--output OUTPUT]
                       [--no-plot] [--sort SORT] [--max-dimension MAX_DIM]
                       [--dpi DPI]
                       image

Arguments:
  image                 Path to the input image

Options:
  -h, --help           Show help message
  --colors, -c         Number of colors to extract (default: 6)
  --method, -m         Extraction method (default: lab)
  --output, -o         Output file path
  --no-plot            Disable plot generation (console output only)
  --sort               Color sorting: spatial-x, spatial-y, frequency, none
  --max-dimension      Max dimension for downscaling (default: 64)
  --dpi                DPI for output plots (default: 150)
```

## Performance Tips

1. **Image Downscaling**: Large images are automatically downscaled for faster processing. Adjust with `--max-dimension`.

2. **Method Selection**:
   - Use `kmeans` for fastest extraction
   - Use `lab` (default) for best perceptual results
   - Use `aggressive` or `vibrant` for images with subtle accent colors

3. **Batch Processing**:
```python
import glob
import color_extractor

for image_path in glob.glob('images/*.jpg'):
    colors = color_extractor.extract_colors(image_path, n_colors=5)
    # Process colors...
```

## Requirements

- Python >= 3.7
- numpy >= 1.19.0
- scikit-learn >= 0.24.0
- scikit-image >= 0.18.0
- Pillow >= 8.0.0
- matplotlib >= 3.3.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by the need for better color extraction in creative coding
- Built for compatibility with TouchDesigner and general Python usage
- Uses scikit-learn for robust K-Means clustering
- Claude generated docs and project structure
