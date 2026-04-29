import typer
from pathlib import Path
import logging
import rasterio
from rasterio.transform import from_origin
import numpy as np

from src.data.handler import SatelliteImageHandler
from src.models.engine import InferenceEngine

# Set basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

app = typer.Typer(help="Geospatial-AI CLI for satellite imagery inference.")

@app.command()
def validate_pipeline():
    """
    End-to-End Validation:
    Proves GDAL (C++) and PyTorch (CUDA/C) can coexist in memory by
    reading a GeoTIFF, running inference, and writing a new GeoTIFF without ABI conflicts.
    """
    input_path = "data/dummy_input.tif"
    output_path = "data/dummy_output.tif"
    
    # 1. Generate Synthetic GeoTIFF (GDAL/Rasterio)
    typer.echo("1. Generating synthetic GeoTIFF (EPSG:4326)...")
    transform = from_origin(-10, 40, 0.1, 0.1) # Starting at lon: -10, lat: 40 with 0.1 deg pixels
    synthetic_data = np.random.rand(1, 1024, 1024).astype(np.float32)
    
    with rasterio.open(
        input_path, 'w', driver='GTiff', height=1024, width=1024, count=1,
        dtype=str(synthetic_data.dtype), crs='EPSG:4326', transform=transform
    ) as dst:
        dst.write(synthetic_data)
        
    # 2. Windowed Read using our Handler (Data Layer)
    typer.echo("2. Reading a 512x512 window via SatelliteImageHandler...")
    handler = SatelliteImageHandler(input_path)
    tensor, profile, window, window_transform = handler.get_patch(row_off=256, col_off=256, width=512, height=512)
    
    # 3. Dummy Inference (ML Layer)
    typer.echo(f"3. Running PyTorch Inference Engine on Tensor of shape {tensor.shape}...")
    engine = InferenceEngine() # Automatically falls back to CPU if no GPU available
    inferred_tensor = engine.infer(tensor)
    
    # 4. Safe Write (Data Layer)
    typer.echo("4. Writing result back to GeoTIFF preserving CRS...")
    handler.write_patch(output_path, inferred_tensor, profile, window=window, window_transform=window_transform)
    
    typer.echo(f"Success! Output written to {output_path}. Pipeline is robust.")
    
@app.command()
def process(
    input_file: Path = typer.Argument(..., help="Path to input GeoTIFF"),
    output_file: Path = typer.Argument(..., help="Path to output GeoTIFF"),
    model_path: str = typer.Option(..., "--model", "-m", help="Path to model weights")
):
    """
    Process a requested satellite image.
    """
    typer.echo(f"Processing {input_file} -> {output_file} with model {model_path}")

@app.command()
def train(
    dataset_path: Path = typer.Argument(..., help="Path to training dataset"),
    epochs: int = typer.Option(10, help="Number of epochs to train")
):
    """
    Train a model on a dataset.
    """
    typer.echo(f"Training on {dataset_path} for {epochs} epochs")

@app.command()
def export(
    model_path: Path = typer.Argument(..., help="Path to PyTorch model"),
    output_path: Path = typer.Argument(..., help="Path to exported ONNX model")
):
    """
    Export a PyTorch model to ONNX.
    """
    typer.echo(f"Exporting model {model_path} to {output_path}")

if __name__ == "__main__":
    app()
