#!/usr/bin/env python3
"""
Example: TouchDesigner integration for color extraction.

This script shows how to use color-extractor within TouchDesigner
for real-time color analysis and palette generation.
"""

import color_extractor


class ColorExtractorExt:
    """
    TouchDesigner extension for color extraction from TOPs.
    
    Usage:
    1. Create a Base COMP in TouchDesigner
    2. Add this as an extension
    3. Connect an input TOP
    4. Call Extract() method or set up automatic extraction
    """
    
    def __init__(self, owner_comp):
        self.owner_comp = owner_comp
        self.colors = []
        self.hex_colors = []
        self.stats = []
        self.cache = {}
        
        # Parameters
        self.method = 'lab'
        self.n_colors = 6
        self.sort_by = 'spatial-x'
        self.max_dimension = 64
    
    def Setup(self):
        """Initialize the extension."""
        # Create custom parameters if needed
        page = self.owner_comp.appendCustomPage('Color Extractor')
        
        # Add method selector
        p = page.appendMenu('Method')[0]
        p.menuNames = ['kmeans', 'aggressive', 'vibrant', 'lab', 'multistage']
        p.menuLabels = ['K-Means', 'Aggressive', 'Vibrant', 'LAB Enhanced', 'Multi-stage']
        p.default = 'lab'
        
        # Add number of colors
        p = page.appendInt('Ncolors')[0]
        p.default = 6
        p.min = 2
        p.max = 12
        p.clampMin = True
        p.clampMax = True
        
        # Add sorting method
        p = page.appendMenu('Sorting')[0]
        p.menuNames = ['spatial-x', 'spatial-y', 'frequency', 'none']
        p.menuLabels = ['Spatial X', 'Spatial Y', 'Frequency', 'None']
        p.default = 'spatial-x'
    
    def Extract(self, input_top=None, use_cache=True):
        """
        Extract colors from a TouchDesigner TOP.
        
        Args:
            input_top: TOP operator to extract from (or uses connected input)
            use_cache: Whether to use cached results for unchanged TOPs
        
        Returns:
            List of hex color strings
        """
        # Get input TOP
        if input_top is None:
            input_top = self.owner_comp.inputs[0]
        
        if not input_top:
            print("No input TOP connected")
            return []
        
        # Check cache
        cache_key = f"{input_top.path}_{input_top.totalCooks}_{self.method}_{self.n_colors}"
        if use_cache and cache_key in self.cache:
            self.colors, self.hex_colors, self.stats = self.cache[cache_key]
            return self.hex_colors
        
        # Get pixels from TOP (TouchDesigner returns 0-1 range)
        pixels = input_top.numpyArray(delayed=True)
        
        # TouchDesigner returns shape (height, width, channels)
        # but channels might be in different order, so we ensure RGB
        if len(pixels.shape) == 3:
            if pixels.shape[2] == 4:  # RGBA
                pixels = pixels[:, :, :3]  # Take only RGB
            elif pixels.shape[2] == 1:  # Grayscale
                pixels = np.repeat(pixels, 3, axis=2)
        
        # Convert from 0-1 to 0-255 range
        img_array = color_extractor.normalize_image_array(
            pixels,
            input_range=(0, 1),
            output_range=(0, 255)
        )
        
        # Downscale if needed
        height, width = img_array.shape[:2]
        if max(height, width) > self.max_dimension:
            from PIL import Image
            import numpy as np
            
            img = Image.fromarray(img_array.astype(np.uint8))
            ratio = self.max_dimension / max(height, width)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            img_array = np.array(img)
        
        # Extract colors
        self.colors, self.stats = color_extractor.extract_colors(
            img_array,
            method=self.method,
            n_colors=self.n_colors,
            sort_by=self.sort_by,
            return_stats=True
        )
        
        # Convert to hex
        self.hex_colors = [color_extractor.rgb_to_hex(c) for c in self.colors]
        
        # Cache results
        self.cache[cache_key] = (self.colors, self.hex_colors, self.stats)
        
        # Update table if connected
        self._update_table()
        
        return self.hex_colors
    
    def _update_table(self):
        """Update connected Table DAT with color information."""
        table_dat = self.owner_comp.op('color_table')
        if not table_dat:
            return
        
        table_dat.clear()
        table_dat.appendRow(['Index', 'Hex', 'R', 'G', 'B', 'Coverage', 'Saturation'])
        
        for i, (color, stat) in enumerate(zip(self.colors, self.stats)):
            r, g, b = color
            table_dat.appendRow([
                str(i),
                stat['hex'],
                str(int(r)),
                str(int(g)),
                str(int(b)),
                f"{stat['percentage']:.1f}%",
                f"{stat['saturation']:.2f}"
            ])
    
    def Get_Color_CHOP(self):
        """
        Create CHOP channels for the extracted colors.
        Can be used with a Script CHOP.
        """
        import numpy as np
        
        if not self.colors:
            return np.array([[]])
        
        # Create channels for R, G, B values (normalized to 0-1)
        channels = []
        for i, color in enumerate(self.colors):
            r, g, b = [c / 255.0 for c in color]
            channels.extend([r, g, b])
        
        return np.array(channels).reshape(-1, 1)
    
    def Apply_To_Ramp(self, ramp_top_name='ramp1'):
        """
        Apply extracted colors to a Ramp TOP.
        
        Args:
            ramp_top_name: Name of the Ramp TOP to update
        """
        ramp = self.owner_comp.op(ramp_top_name)
        if not ramp:
            print(f"Ramp TOP '{ramp_top_name}' not found")
            return
        
        # Clear existing keys
        for i in range(8):
            setattr(ramp.par, f'colorr{i}', 0)
            setattr(ramp.par, f'colorg{i}', 0)
            setattr(ramp.par, f'colorb{i}', 0)
        
        # Set new colors
        for i, color in enumerate(self.colors[:8]):  # Ramp supports up to 8 keys
            r, g, b = [c / 255.0 for c in color]
            setattr(ramp.par, f'colorr{i}', r)
            setattr(ramp.par, f'colorg{i}', g)
            setattr(ramp.par, f'colorb{i}', b)
            setattr(ramp.par, f'colorpos{i}', i / max(1, len(self.colors) - 1))
    
    def On_Parameter_Change(self, par, val):
        """Called when a custom parameter changes."""
        if par.name == 'Method':
            self.method = val
            self.cache.clear()
        elif par.name == 'Ncolors':
            self.n_colors = int(val)
            self.cache.clear()
        elif par.name == 'Sorting':
            self.sort_by = val
            self.cache.clear()
    
    def Cook(self):
        """Called when the component cooks."""
        # Auto-extract if input has changed
        if self.owner_comp.inputs[0]:
            self.Extract()


# Example usage in TouchDesigner Execute DAT
def on_frame_start():
    """
    Example of using the extractor on every frame.
    Put this in an Execute DAT set to "Frame Start"
    """
    extractor = op('base_color_extractor')
    if extractor and extractor.inputs[0]:
        colors = extractor.Extract()
        
        # Use the colors for something
        # For example, set background color to dominant color
        if colors:
            dominant = colors[0]
            # Convert hex to RGB for TouchDesigner (0-1 range)
            r = int(dominant[1:3], 16) / 255
            g = int(dominant[3:5], 16) / 255
            b = int(dominant[5:7], 16) / 255
            
            # Set a Constant TOP's color
            constant = op('constant1')
            if constant:
                constant.par.colorr = r
                constant.par.colorg = g
                constant.par.colorb = b


# Standalone test function
def test_with_image():
    """Test the color extraction with a sample image."""
    import numpy as np
    
    # Create a test image with distinct color regions
    img = np.zeros((100, 150, 3), dtype=np.float32)
    
    # Red region
    img[0:50, 0:50] = [1.0, 0.0, 0.0]
    
    # Green region
    img[0:50, 50:100] = [0.0, 1.0, 0.0]
    
    # Blue region
    img[50:100, 0:50] = [0.0, 0.0, 1.0]
    
    # Yellow region
    img[50:100, 50:100] = [1.0, 1.0, 0.0]
    
    # Purple region
    img[0:100, 100:150] = [0.5, 0.0, 0.5]
    
    # Convert to 0-255 range
    img_255 = color_extractor.normalize_image_array(
        img,
        input_range=(0, 1),
        output_range=(0, 255)
    )
    
    # Extract colors
    colors = color_extractor.extract_colors(img_255, method='lab', n_colors=5)
    
    print("Extracted colors:")
    for i, color in enumerate(colors, 1):
        hex_color = color_extractor.rgb_to_hex(color)
        print(f"  {i}. {hex_color} - RGB{tuple(int(c) for c in color)}")


if __name__ == "__main__":
    # Run test when script is executed directly
    test_with_image()
