import torch
import torch.nn as nn
import logging

class DummyModel(nn.Module):
    """
    A fake PyTorch model for testing the pipeline architecture
    without needing heavy pre-trained weights.
    """
    def __init__(self, channels=1):
        super().__init__()
        # Simple convolution that won't change spatial dimensions
        self.conv = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.conv(x))

class InferenceEngine:
    """
    Handles PyTorch model loading and execution on GPU/CPU.
    """
    def __init__(self, model_path: str = None, device: str = None):
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        logging.info(f"Initializing InferenceEngine on {self.device}")
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        """
        Loads the actual model. For boilerplate testing, we load the DummyModel.
        """
        # We will load the actual model here in production:
        # self.model = torch.load(self.model_path).to(self.device)
        logging.info("Loading DummyModel for validation.")
        self.model = DummyModel(channels=1).to(self.device)
        self.model.eval()

    def infer(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Run inference on a single tensor patch.
        Simulates moving data to GPU, processing, and bringing it back.
        """
        # PyTorch demands a batch dimension: (Batch, Channels, Height, Width)
        # Assuming input is (Channels, Height, Width) from Rasterio
        tensor = tensor.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(tensor)
            
        # Remove batch dimension
        output = output.squeeze(0)
        return output

