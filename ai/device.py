"""
Device utilities for PyTorch with macOS Metal (MPS) support.

Provides cross-platform device detection for CUDA, MPS (Metal), and CPU.
"""

import torch


def get_best_device() -> torch.device:
    """
    Get the best available device for PyTorch operations.
    
    Priority: CUDA > MPS (Metal) > CPU
    
    Returns:
        torch.device: The best available device
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def get_device_info() -> dict:
    """
    Get information about available devices.
    
    Returns:
        dict: Device availability info
    """
    info = {
        'cuda_available': torch.cuda.is_available(),
        'mps_available': hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(),
        'best_device': str(get_best_device()),
    }
    
    if info['cuda_available']:
        info['cuda_device_name'] = torch.cuda.get_device_name(0)
        info['cuda_device_count'] = torch.cuda.device_count()
    
    return info


def print_device_info():
    """Print device availability information."""
    info = get_device_info()
    print(f"Device Info:")
    print(f"  CUDA available: {info['cuda_available']}")
    print(f"  MPS (Metal) available: {info['mps_available']}")
    print(f"  Best device: {info['best_device']}")
    if info['cuda_available']:
        print(f"  CUDA device: {info['cuda_device_name']}")


if __name__ == "__main__":
    print_device_info()
