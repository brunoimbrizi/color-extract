#!/usr/bin/env python3
"""
Example: Batch process multiple images and create a color catalog.
"""

import os
import json
import color_extractor
from pathlib import Path


def process_image_directory(directory_path, output_file='color_catalog.json'):
    """
    Process all images in a directory and create a color catalog.
    
    Args:
        directory_path: Path to directory containing images
        output_file: Output JSON file for the catalog
    """
    results = {}
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    # Find all images
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(directory_path).glob(f'*{ext}'))
        image_files.extend(Path(directory_path).glob(f'*{ext.upper()}'))
    
    print(f"Found {len(image_files)} images to process")
    
    for image_path in image_files:
        print(f"\nProcessing: {image_path.name}")
        
        try:
            # Extract colors with statistics
            colors, stats = color_extractor.extract_colors(
                str(image_path),
                method='lab',
                n_colors=5,
                sort_by='spatial-x',
                return_stats=True
            )
            
            # Store results
            results[image_path.name] = {
                'colors': [stat['hex'] for stat in stats],
                'statistics': stats,
                'dominant_color': stats[0]['hex'] if stats else None
            }
            
            print(f"  Dominant color: {stats[0]['hex']}")
            
        except Exception as e:
            print(f"  Error processing {image_path.name}: {e}")
            results[image_path.name] = {'error': str(e)}
    
    # Save catalog
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nColor catalog saved to: {output_file}")
    return results


def create_html_palette_viewer(catalog_file='color_catalog.json', output_file='palette_viewer.html'):
    """
    Create an HTML file to view the extracted color palettes.
    
    Args:
        catalog_file: JSON file with color catalog
        output_file: Output HTML file
    """
    with open(catalog_file, 'r') as f:
        catalog = json.load(f)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Color Palette Viewer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f0f0;
                padding: 20px;
            }
            .image-palette {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .image-name {
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            .color-swatches {
                display: flex;
                gap: 5px;
                margin-bottom: 10px;
            }
            .color-swatch {
                width: 80px;
                height: 60px;
                border-radius: 4px;
                display: flex;
                align-items: flex-end;
                justify-content: center;
                color: white;
                font-size: 11px;
                text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
                padding-bottom: 4px;
                border: 1px solid #ddd;
            }
            .stats {
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>Extracted Color Palettes</h1>
    """
    
    for image_name, data in catalog.items():
        if 'error' in data:
            continue
            
        html += f'<div class="image-palette">'
        html += f'<div class="image-name">{image_name}</div>'
        html += '<div class="color-swatches">'
        
        for stat in data.get('statistics', []):
            hex_color = stat['hex']
            percentage = stat['percentage']
            html += f'''
                <div class="color-swatch" style="background-color: {hex_color};">
                    {hex_color}
                </div>
            '''
        
        html += '</div>'
        html += '<div class="stats">'
        for i, stat in enumerate(data.get('statistics', []), 1):
            html += f"Color {i}: ~{stat['percentage']}% | "
        html += '</div>'
        html += '</div>'
    
    html += """
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"HTML viewer saved to: {output_file}")


def compare_methods_on_image(image_path, output_path='method_comparison.json'):
    """
    Compare all extraction methods on a single image.
    
    Args:
        image_path: Path to the image
        output_path: Output file for comparison results
    """
    methods = ['kmeans', 'aggressive', 'vibrant', 'lab', 'multistage']
    results = {}
    
    print(f"Comparing extraction methods on: {image_path}")
    
    for method in methods:
        print(f"\nTesting method: {method}")
        colors, stats = color_extractor.extract_colors(
            image_path,
            method=method,
            n_colors=6,
            sort_by='spatial-x',
            return_stats=True
        )
        
        results[method] = {
            'colors': [stat['hex'] for stat in stats],
            'dominant': stats[0] if stats else None
        }
        
        print(f"  Colors: {', '.join(stat['hex'] for stat in stats[:3])}...")
    
    # Save comparison
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nComparison saved to: {output_path}")
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python batch_processing.py <directory>  # Process all images in directory")
        print("  python batch_processing.py <image>      # Compare methods on single image")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isdir(path):
        # Process directory
        catalog = process_image_directory(path)
        create_html_palette_viewer()
    elif os.path.isfile(path):
        # Compare methods on single image
        compare_methods_on_image(path)
    else:
        print(f"Error: {path} not found")
