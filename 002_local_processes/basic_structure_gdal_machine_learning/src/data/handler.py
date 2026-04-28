import rasterio
from rasterio.windows import Window
import torch
import numpy as np

class SatelliteImageHandler:
    """
    Handles reading and writing of satellite imagery using windowed operations
    to conserve memory. Strictly preserves CRS and Geotransforms.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_patch(self, row_off: int, col_off: int, width: int, height: int):
        """
        Extracts a patch (tile) from the image as a PyTorch Tensor
        and returns the specific transform for this window.
        """
        with rasterio.open(self.filepath) as src:
            window = Window(col_off, row_off, width, height)
            data = src.read(window=window)
            window_transform = src.window_transform(window)
            profile = src.profile
            
            # Convert to PyTorch Tensor (Channels, Height, Width)
            # Depending on the dtype, we might need to normalize later.
            tensor = torch.from_numpy(data.astype(np.float32))
            
            return tensor, profile, window, window_transform

    def write_patch(self, output_path: str, tensor: torch.Tensor, profile: dict, window: Window=None, window_transform=None):
        """
        Writes a single PyTorch Tensor patch back to a TIFF file safely,
        injecting the correct EPSG/CRS and transform.
        """
        # Convert back to numpy (Host memory)
        data = tensor.cpu().numpy()
        
        # Override profile with specific window settings if provided
        out_profile = profile.copy()
        out_profile.update(
            dtype=data.dtype.name,
            count=data.shape[0], # Channels
        )
        
        # If it's just a patch of a larger file, adjust the transform
        if window_transform is not None:
             out_profile.update(
                height=window.height,
                width=window.width,
                transform=window_transform
             )
             
        # Write to disk preserving GIS metadata
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            if window is not None and window_transform is None:
                # If writing to a very large pre-existing file
                dst.write(data, window=window)
            else:
                # If writing a brand new standalone patch file
                dst.write(data)

